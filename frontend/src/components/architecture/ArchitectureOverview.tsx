import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
  Position,
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

type ArchitectureOverviewProps = {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
};


// ============================================================
// CATEGORY CONFIG
// ============================================================

const CATEGORY_CONFIG = {
  router: {
    label: "Routing",
    description: "Navigation and route definitions",
  },

  page: {
    label: "Pages",
    description: "Application screens and pages",
  },

  component: {
    label: "Components",
    description: "Reusable UI components",
  },

  context: {
    label: "Context",
    description: "Shared application state",
  },

  hook: {
    label: "Hooks",
    description: "Reusable React logic",
  },

  utility: {
    label: "Utilities",
    description: "Helper and utility modules",
  },

  config: {
    label: "Configuration",
    description: "Build and project configuration",
  },

  source: {
    label: "Source",
    description: "Other source modules",
  },
} as const;

type Category =
  keyof typeof CATEGORY_CONFIG;


// ============================================================
// HELPERS
// ============================================================

function normalizeCategory(
  category?: string
): Category {
  if (
    category &&
    category in CATEGORY_CONFIG
  ) {
    return category as Category;
  }

  return "source";
}


function countByCategory(
  nodes: DependencyNode[]
) {
  const counts: Record<Category, number> = {
    router: 0,
    page: 0,
    component: 0,
    context: 0,
    hook: 0,
    utility: 0,
    config: 0,
    source: 0,
  };

  for (const node of nodes) {
    const category = normalizeCategory(
      node.category
    );

    counts[category] += 1;
  }

  return counts;
}


// ============================================================
// ARCHITECTURE NODES
// ============================================================

function buildArchitectureNodes(
  nodes: DependencyNode[]
): Node[] {
  const counts = countByCategory(nodes);

  const definitions: Array<{
    id: Category;
    x: number;
    y: number;
  }> = [
    {
      id: "router",
      x: 0,
      y: 80,
    },
    {
      id: "page",
      x: 360,
      y: 80,
    },
    {
      id: "component",
      x: 720,
      y: 80,
    },
    {
      id: "context",
      x: 180,
      y: 300,
    },
    {
      id: "hook",
      x: 540,
      y: 300,
    },
    {
      id: "utility",
      x: 900,
      y: 300,
    },
    {
      id: "config",
      x: 360,
      y: 520,
    },
    {
      id: "source",
      x: 720,
      y: 520,
    },
  ];

  return definitions
    .filter(
      (definition) =>
        counts[definition.id] > 0
    )
    .map((definition) => {
      const config =
        CATEGORY_CONFIG[definition.id];

      return {
        id: definition.id,

        position: {
          x: definition.x,
          y: definition.y,
        },

        sourcePosition: Position.Right,
        targetPosition: Position.Left,

        data: {
          label: (
            <div className="space-y-2">

              <div className="text-sm font-semibold text-white">
                {config.label}
              </div>

              <div className="text-xs leading-5 text-slate-400">
                {config.description}
              </div>

              <div className="pt-1 text-lg font-bold text-blue-400">
                {counts[definition.id]}
              </div>

              <div className="text-[10px] uppercase tracking-wider text-slate-500">
                files
              </div>

            </div>
          ),
        },

        style: {
          width: 220,
          minHeight: 125,
          borderRadius: 16,
          border: "1px solid #334155",
          background: "#0f172a",
          color: "#ffffff",
          padding: "16px",
          boxShadow:
            "0 10px 30px rgba(0, 0, 0, 0.30)",
        },
      };
    });
}


// ============================================================
// ARCHITECTURE EDGES
// ============================================================

function buildArchitectureEdges(
  nodes: DependencyNode[],
  edges: DependencyEdge[]
): Edge[] {
  const nodeCategory = new Map<
    string,
    Category
  >();

  for (const node of nodes) {
    nodeCategory.set(
      node.id,
      normalizeCategory(node.category)
    );
  }

  const categoryRelationships = new Map<
    string,
    number
  >();

  for (const edge of edges) {
    const sourceCategory =
      nodeCategory.get(edge.source);

    const targetCategory =
      nodeCategory.get(edge.target);

    if (
      !sourceCategory ||
      !targetCategory ||
      sourceCategory === targetCategory
    ) {
      continue;
    }

    const key =
      `${sourceCategory}->${targetCategory}`;

    categoryRelationships.set(
      key,
      (categoryRelationships.get(key) || 0) + 1
    );
  }

  return Array.from(
    categoryRelationships.entries()
  ).map(
    ([relationship, count], index) => {
      const [
        source,
        target,
      ] = relationship.split(
        "->"
      ) as [Category, Category];

      return {
        id: `architecture-${index}`,

        source,
        target,

        type: "smoothstep",

        animated: false,

        style: {
          stroke:
            count > 2
              ? "#3b82f6"
              : "#475569",

          strokeWidth:
            count > 2
              ? 2.5
              : 1.5,
        },

        markerEnd: {
          type: "arrowclosed",
          color:
            count > 2
              ? "#3b82f6"
              : "#64748b",
          width: 16,
          height: 16,
        },

        label:
          count > 1
            ? `${count} dependencies`
            : undefined,

        labelStyle: {
          fill: "#94a3b8",
          fontSize: 9,
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
      };
    }
  );
}


// ============================================================
// EMPTY STATE
// ============================================================

function EmptyArchitecture() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-8">

      <h3 className="text-lg font-semibold text-white">
        Architecture Overview
      </h3>

      <p className="mt-2 text-sm text-slate-500">
        Not enough structural information was found
        to build an architecture overview.
      </p>

    </div>
  );
}


// ============================================================
// MAIN COMPONENT
// ============================================================

function ArchitectureOverview({
  nodes,
  edges,
}: ArchitectureOverviewProps) {
  const flowNodes =
    buildArchitectureNodes(nodes);

  const flowEdges =
    buildArchitectureEdges(
      nodes,
      edges
    );

  if (flowNodes.length === 0) {
    return <EmptyArchitecture />;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">

      <div
        className="w-full"
        style={{ height: "620px" }}
      >
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          fitView
          fitViewOptions={{
            padding: 0.25,
            minZoom: 0.4,
            maxZoom: 1.3,
          }}
          defaultEdgeOptions={{
            type: "smoothstep",
          }}
          attributionPosition="bottom-left"
        >

          <Background
            gap={20}
            size={1}
            color="#1e293b"
          />

          <Controls />

        </ReactFlow>
      </div>

    </div>
  );
}

export default ArchitectureOverview;