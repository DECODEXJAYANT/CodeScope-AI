import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  Position,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";


// ============================================================
// TYPES
// ============================================================

type DependencyNode = {
  id: string;
  type: string;
  label: string;
  category?: string;
  path?: string;
};

type DependencyEdge = {
  source: string;
  target: string;
  import?: string;
};

type DependencyGraphProps = {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
};


// ============================================================
// CATEGORY CONFIGURATION
// ============================================================

type CategoryConfig = {
  title: string;
  description: string;
  border: string;
  background: string;
  text: string;
};

const CATEGORY_CONFIG: Record<string, CategoryConfig> = {
  page: {
    title: "Page",
    description: "Application page",
    border: "#2563eb",
    background: "#0f172a",
    text: "#60a5fa",
  },

  component: {
    title: "Component",
    description: "Reusable UI component",
    border: "#7c3aed",
    background: "#0f172a",
    text: "#a78bfa",
  },

  hook: {
    title: "Hook",
    description: "Reusable React hook",
    border: "#0891b2",
    background: "#0f172a",
    text: "#22d3ee",
  },

  context: {
    title: "Context",
    description: "Application state",
    border: "#059669",
    background: "#0f172a",
    text: "#34d399",
  },

  router: {
    title: "Router",
    description: "Routing module",
    border: "#d97706",
    background: "#0f172a",
    text: "#fbbf24",
  },

  utility: {
    title: "Utility",
    description: "Utility module",
    border: "#db2777",
    background: "#0f172a",
    text: "#f472b6",
  },

  config: {
    title: "Config",
    description: "Configuration file",
    border: "#475569",
    background: "#0f172a",
    text: "#94a3b8",
  },

  source: {
    title: "Source",
    description: "Source file",
    border: "#334155",
    background: "#0f172a",
    text: "#e2e8f0",
  },
};


// ============================================================
// HELPERS
// ============================================================

function getCategoryConfig(
  category?: string
): CategoryConfig {
  return (
    CATEGORY_CONFIG[category || "source"] ||
    CATEGORY_CONFIG.source
  );
}


function getNodeColumn(category?: string): number {
  switch (category) {
    case "router":
      return 0;

    case "page":
      return 1;

    case "component":
      return 2;

    case "context":
    case "hook":
      return 3;

    case "utility":
      return 4;

    case "config":
      return 5;

    default:
      return 2;
  }
}


// ============================================================
// BUILD NODE POSITIONS
// ============================================================

function buildFlowNodes(
  nodes: DependencyNode[]
): Node[] {
  const groupedNodes = new Map<
    number,
    DependencyNode[]
  >();

  for (const node of nodes) {
    const column = getNodeColumn(node.category);

    if (!groupedNodes.has(column)) {
      groupedNodes.set(column, []);
    }

    groupedNodes.get(column)!.push(node);
  }

  const flowNodes: Node[] = [];

  const columnWidth = 290;
  const rowHeight = 145;

  for (const [column, columnNodes] of groupedNodes) {
    columnNodes.sort((a, b) =>
      a.label.localeCompare(b.label)
    );

    columnNodes.forEach((node, index) => {
      const categoryConfig = getCategoryConfig(
        node.category
      );

      flowNodes.push({
        id: node.id,

        position: {
          x: column * columnWidth,
          y: index * rowHeight,
        },

        sourcePosition: Position.Right,
        targetPosition: Position.Left,

        data: {
          label: (
            <div className="space-y-1">
              <div
                style={{
                  color: categoryConfig.text,
                  fontSize: 10,
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                }}
              >
                {categoryConfig.title}
              </div>

              <div
                style={{
                  color: "#f8fafc",
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                {node.label}
              </div>

              <div
                style={{
                  color: "#64748b",
                  fontSize: 10,
                  lineHeight: 1.4,
                }}
              >
                {node.path || node.id}
              </div>
            </div>
          ),
        },

        style: {
          width: 235,
          minHeight: 82,
          background: categoryConfig.background,
          color: "#ffffff",
          border: `1px solid ${categoryConfig.border}`,
          borderRadius: 14,
          padding: "12px 14px",
          boxShadow:
            "0 8px 24px rgba(0, 0, 0, 0.25)",
        },
      });
    });
  }

  return flowNodes;
}


// ============================================================
// BUILD EDGES
// ============================================================

function buildFlowEdges(
  edges: DependencyEdge[]
): Edge[] {
  return edges.map((edge, index) => ({
    id: `${edge.source}-${edge.target}-${index}`,

    source: edge.source,
    target: edge.target,

    type: "smoothstep",

    animated: false,

    style: {
      stroke: "#475569",
      strokeWidth: 1.6,
    },

    markerEnd: {
      type: "arrowclosed",
      color: "#64748b",
      width: 16,
      height: 16,
    },

    ...(edge.import
      ? {
          label: edge.import,

          labelStyle: {
            fill: "#94a3b8",
            fontSize: 9,
            fontWeight: 500,
          },

          labelBgStyle: {
            fill: "#020617",
            fillOpacity: 0.95,
          },

          labelBgPadding: [
            4,
            2,
          ] as [number, number],

          labelBgBorderRadius: 4,
        }
      : {}),
  }));
}


// ============================================================
// LEGEND
// ============================================================

function GraphLegend() {
  const categories = [
    "router",
    "page",
    "component",
    "context",
    "hook",
    "utility",
    "config",
  ];

  return (
    <div className="absolute right-4 top-4 z-10 w-52 rounded-xl border border-slate-800 bg-slate-950/95 p-4 shadow-xl backdrop-blur">

      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
        File Categories
      </p>

      <div className="space-y-2">

        {categories.map((category) => {
          const config =
            getCategoryConfig(category);

          return (
            <div
              key={category}
              className="flex items-center gap-2"
            >

              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{
                  backgroundColor:
                    config.border,
                }}
              />

              <span className="text-xs text-slate-300">
                {config.title}
              </span>

            </div>
          );
        })}

      </div>
    </div>
  );
}


// ============================================================
// EMPTY STATE
// ============================================================

function EmptyGraph() {
  return (
    <div
      className="flex w-full items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/70"
      style={{
        height: "650px",
      }}
    >
      <div className="max-w-md px-6 text-center">

        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-800 bg-slate-950">
          <span className="text-2xl text-slate-600">
            ∅
          </span>
        </div>

        <p className="text-lg font-semibold text-white">
          No dependencies found
        </p>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          CodeScope AI could not find local
          JavaScript or TypeScript file
          dependencies in the analyzed files.
        </p>

      </div>
    </div>
  );
}


// ============================================================
// MAIN COMPONENT
// ============================================================

function DependencyGraph({
  nodes,
  edges,
}: DependencyGraphProps) {
  const flowNodes = buildFlowNodes(nodes);
  const flowEdges = buildFlowEdges(edges);

  if (flowNodes.length === 0) {
    return <EmptyGraph />;
  }

  return (
    <div
      className="relative w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950"
      style={{
        height: "700px",
      }}
    >

      <GraphLegend />

      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        fitView
        fitViewOptions={{
          padding: 0.25,
          minZoom: 0.4,
          maxZoom: 1.4,
        }}
        defaultEdgeOptions={{
          type: "smoothstep",
        }}
        proOptions={{
          hideAttribution: false,
        }}
        attributionPosition="bottom-left"
      >

        <Background
          gap={20}
          size={1}
          color="#1e293b"
        />

        <Controls
          showInteractive={false}
        />

        <MiniMap
          nodeColor={(node) => {
            const category =
              node.data?.category;

            return getCategoryConfig(
              typeof category === "string"
                ? category
                : "source"
            ).border;
          }}
          maskColor="rgba(2, 6, 23, 0.75)"
          pannable
          zoomable
        />

      </ReactFlow>
    </div>
  );
}

export default DependencyGraph;