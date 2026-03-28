import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execSync } from "child_process";
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from "fs";
import { join, resolve } from "path";

const WORKSPACE = resolve("D:/SeAAI/NAEL");
const KNOWLEDGE_DIR = join(WORKSPACE, "knowledge");
const TOOLS_DIR = join(WORKSPACE, "tools");

const server = new McpServer({
  name: "nael",
  version: "0.1.0",
});

// ========== Tool 1: Knowledge Store ==========
// 지식을 구조화하여 저장/조회
server.tool(
  "knowledge_store",
  "Store structured knowledge to the NAEL knowledge base",
  {
    title: z.string().describe("Knowledge entry title"),
    content: z.string().describe("Knowledge content (markdown)"),
    domain: z.string().describe("Domain: ai, quantum, robotics, bio, general, etc."),
    tags: z.string().describe("Comma-separated tags"),
    source: z.string().optional().describe("Source URL or reference"),
  },
  async ({ title, content, domain, tags, source }) => {
    if (!existsSync(KNOWLEDGE_DIR)) mkdirSync(KNOWLEDGE_DIR, { recursive: true });
    const domainDir = join(KNOWLEDGE_DIR, domain);
    if (!existsSync(domainDir)) mkdirSync(domainDir, { recursive: true });

    const filename = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") + ".md";
    const filepath = join(domainDir, filename);

    const tagList = tags.split(",").map((t) => t.trim());
    const entry = `---
title: ${title}
domain: ${domain}
tags: [${tagList.join(", ")}]
date: ${new Date().toISOString().split("T")[0]}
${source ? `source: ${source}` : ""}
---

${content}
`;
    writeFileSync(filepath, entry, "utf-8");
    return { content: [{ type: "text", text: `Stored: ${filepath}` }] };
  }
);

// ========== Tool 2: Knowledge Search ==========
server.tool(
  "knowledge_search",
  "Search the NAEL knowledge base by keyword, domain, or tags",
  {
    query: z.string().describe("Search query (keyword match in title/content/tags)"),
    domain: z.string().optional().describe("Filter by domain"),
  },
  async ({ query, domain }) => {
    if (!existsSync(KNOWLEDGE_DIR)) {
      return { content: [{ type: "text", text: "Knowledge base is empty." }] };
    }

    const results = [];
    const searchDirs = domain
      ? [join(KNOWLEDGE_DIR, domain)]
      : readdirSync(KNOWLEDGE_DIR, { withFileTypes: true })
          .filter((d) => d.isDirectory())
          .map((d) => join(KNOWLEDGE_DIR, d.name));

    const queryLower = query.toLowerCase();
    for (const dir of searchDirs) {
      if (!existsSync(dir)) continue;
      for (const file of readdirSync(dir)) {
        if (!file.endsWith(".md")) continue;
        const content = readFileSync(join(dir, file), "utf-8");
        if (content.toLowerCase().includes(queryLower)) {
          // Extract title from frontmatter
          const titleMatch = content.match(/^title:\s*(.+)$/m);
          const title = titleMatch ? titleMatch[1] : file;
          results.push({
            title,
            path: join(dir, file),
            snippet: content.substring(0, 200),
          });
        }
      }
    }

    if (results.length === 0) {
      return { content: [{ type: "text", text: `No results for "${query}"` }] };
    }

    const output = results
      .map((r) => `### ${r.title}\nPath: ${r.path}\n${r.snippet}...`)
      .join("\n\n---\n\n");

    return { content: [{ type: "text", text: `Found ${results.length} results:\n\n${output}` }] };
  }
);

// ========== Tool 3: Capability Scan ==========
server.tool(
  "capability_scan",
  "Scan current workspace capabilities: tools, knowledge, skills",
  {},
  async () => {
    try {
      const result = execSync(`python -X utf8 "${join(TOOLS_DIR, "automation", "self_monitor.py")}" --json`, {
        encoding: "utf-8",
        cwd: WORKSPACE,
      });
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Scan failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 4: Gap Analysis ==========
server.tool(
  "gap_analysis",
  "Analyze capability gaps — what the agent should build next",
  {},
  async () => {
    try {
      const result = execSync(`python -X utf8 "${join(TOOLS_DIR, "automation", "self_monitor.py")}" --gaps`, {
        encoding: "utf-8",
        cwd: WORKSPACE,
      });
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Gap analysis failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 5: Quick Debate ==========
server.tool(
  "quick_debate",
  "Generate a multi-persona debate prompt for any topic",
  {
    topic: z.string().describe("Debate topic"),
    preset: z.enum(["default", "tech", "business", "research"]).optional().describe("Persona preset"),
  },
  async ({ topic, preset }) => {
    const p = preset || "default";
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "cognitive", "debate.py")}" --topic "${topic.replace(/"/g, '\\"')}" --preset ${p} --mode quick`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Debate generation failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 6: Scaffold Project ==========
server.tool(
  "scaffold_project",
  "Create a project skeleton from template (python-cli, python-lib, node-api, mcp-server, experiment)",
  {
    template: z.string().describe("Template type"),
    name: z.string().describe("Project name"),
    output_dir: z.string().describe("Output directory path"),
    description: z.string().optional().describe("Project description"),
  },
  async ({ template, name, output_dir, description }) => {
    const desc = description || "";
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "automation", "scaffold.py")}" --type ${template} --name "${name}" --output "${output_dir}" --description "${desc}"`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Scaffold failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 7: Evolution Log ==========
server.tool(
  "evolution_log",
  "Read or append to the evolution log",
  {
    action: z.enum(["read", "append"]).describe("Read the log or append an entry"),
    entry: z.string().optional().describe("Entry to append (markdown)"),
  },
  async ({ action, entry }) => {
    const logPath = join(WORKSPACE, "evolution-log.md");

    if (action === "read") {
      if (!existsSync(logPath)) {
        return { content: [{ type: "text", text: "Evolution log is empty." }] };
      }
      const content = readFileSync(logPath, "utf-8");
      return { content: [{ type: "text", text: content }] };
    }

    // append
    if (!entry) {
      return { content: [{ type: "text", text: "No entry provided." }] };
    }
    const existing = existsSync(logPath) ? readFileSync(logPath, "utf-8") : "# Evolution Log\n\n";
    const updated = existing + "\n" + entry + "\n";
    writeFileSync(logPath, updated, "utf-8");
    return { content: [{ type: "text", text: "Entry appended to evolution log." }] };
  }
);

// ========== Tool 8: Experience Store ==========
server.tool(
  "experience_record",
  "Record a problem-solving experience to the experience library for future reuse",
  {
    problem_type: z.enum(["bug_fix", "design", "research", "evolution", "optimization", "integration"]),
    problem: z.string().describe("Problem description"),
    tools: z.string().describe("Comma-separated tool names used"),
    workflow: z.enum(["pipeline", "consensus", "iterative", "single", "parallel"]).optional(),
    outcome: z.enum(["success", "partial", "failure"]).optional(),
    score: z.number().optional().describe("Reward score 0-1"),
    lesson: z.string().optional().describe("One-line lesson learned"),
  },
  async ({ problem_type, problem, tools, workflow, outcome, score, lesson }) => {
    const wf = workflow || "single";
    const oc = outcome || "success";
    const sc = score ?? 1.0;
    const ls = lesson || "";
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "automation", "experience_store.py")}" record --problem-type ${problem_type} --problem "${problem.replace(/"/g, '\\"')}" --tools "${tools}" --workflow ${wf} --outcome ${oc} --score ${sc} --lesson "${ls.replace(/"/g, '\\"')}"`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Record failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 9: Experience Query ==========
server.tool(
  "experience_query",
  "Search past experiences for a similar problem — returns lessons and recommended tool combos",
  {
    keyword: z.string().describe("Search keyword"),
  },
  async ({ keyword }) => {
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "automation", "experience_store.py")}" query --keyword "${keyword.replace(/"/g, '\\"')}"`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result || "No matching experiences found." }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Query failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 10: Guardrail Validate ==========
server.tool(
  "guardrail_validate",
  "Run safety validation on a Python file — checks syntax, dangerous patterns, documentation",
  {
    file_path: z.string().describe("Path to Python file to validate"),
  },
  async ({ file_path }) => {
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "automation", "guardrail.py")}" validate --file "${file_path}"`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Validation failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 11: Guardrail Checkpoint ==========
server.tool(
  "guardrail_checkpoint",
  "Create a rollback point for a file before making changes",
  {
    file_path: z.string().describe("Path to file to checkpoint"),
  },
  async ({ file_path }) => {
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "automation", "guardrail.py")}" checkpoint --file "${file_path}"`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Checkpoint failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 12: Telemetry Report ==========
server.tool(
  "telemetry_report",
  "Generate a telemetry report — tool usage, failure patterns, recommendations",
  {},
  async () => {
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "automation", "telemetry.py")}" report`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Report failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 13: Performance Dashboard ==========
server.tool(
  "perf_dashboard",
  "Generate performance metrics dashboard — tool latency, quality, error rates, rankings",
  {
    tool: z.string().optional().describe("Filter by specific tool name"),
  },
  async ({ tool }) => {
    const toolArg = tool ? ` --tool "${tool}"` : "";
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "automation", "perf_metrics.py")}" dashboard${toolArg}`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Dashboard failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 14: Experiment Create ==========
server.tool(
  "experiment_create",
  "Design a new hypothesis-driven experiment",
  {
    hypothesis: z.string().describe("Hypothesis to test"),
    iv: z.string().optional().describe("Independent variable"),
    dv: z.string().optional().describe("Dependent variable"),
    prediction: z.string().optional().describe("Expected outcome"),
  },
  async ({ hypothesis, iv, dv, prediction }) => {
    const ivArg = iv ? ` --iv "${iv.replace(/"/g, '\\"')}"` : "";
    const dvArg = dv ? ` --dv "${dv.replace(/"/g, '\\"')}"` : "";
    const predArg = prediction ? ` --prediction "${prediction.replace(/"/g, '\\"')}"` : "";
    try {
      const result = execSync(
        `python -X utf8 "${join(TOOLS_DIR, "cognitive", "hypothesis.py")}" create --hypothesis "${hypothesis.replace(/"/g, '\\"')}"${ivArg}${dvArg}${predArg}`,
        { encoding: "utf-8", cwd: WORKSPACE }
      );
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Experiment creation failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 15: Knowledge Graph ==========
server.tool(
  "knowledge_graph",
  "Show cross-domain knowledge concept graph and gap analysis",
  {
    action: z.enum(["scan", "graph", "gaps", "query"]).describe("scan=rebuild index, graph=show graph, gaps=find gaps, query=search"),
    keyword: z.string().optional().describe("Search keyword (for query action)"),
  },
  async ({ action, keyword }) => {
    let cmd = `python -X utf8 "${join(TOOLS_DIR, "cognitive", "knowledge_index.py")}" ${action}`;
    if (action === "query" && keyword) {
      cmd += ` "${keyword.replace(/"/g, '\\"')}"`;
    }
    try {
      const result = execSync(cmd, { encoding: "utf-8", cwd: WORKSPACE });
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Knowledge graph ${action} failed: ${e.message}` }] };
    }
  }
);

// ========== Tool 16: Source Verify ==========
server.tool(
  "source_verify",
  "Extract verifiable claims from a knowledge document and track verification status",
  {
    action: z.enum(["extract", "status"]).describe("extract=extract claims from file, status=show overall status"),
    file: z.string().optional().describe("File path (for extract action)"),
  },
  async ({ action, file }) => {
    let cmd = `python -X utf8 "${join(TOOLS_DIR, "cognitive", "source_verify.py")}" ${action}`;
    if (action === "extract" && file) {
      cmd += ` --file "${file}"`;
    }
    try {
      const result = execSync(cmd, { encoding: "utf-8", cwd: WORKSPACE });
      return { content: [{ type: "text", text: result }] };
    } catch (e) {
      return { content: [{ type: "text", text: `Source verify ${action} failed: ${e.message}` }] };
    }
  }
);

// ========== Start Server ==========
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("NAEL MCP server running on stdio");
}

main().catch(console.error);
