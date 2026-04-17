# deep_research_mcp.py
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "arxiv>=3.0.0",
#     "duckduckgo-search>=8.0.0",
#     "mcp[cli]>=1.0.0",
# ]
# ///
import arxiv
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("Deep Research Skill")


@mcp.tool()
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for up-to-date information, documentation, and tech articles.
    Use this iteratively: if the first search lacks depth, generate specific queries based on initial results.
    """
    try:
        results = DDGS().text(query, max_results=max_results)
        return "\n\n".join(
            [
                f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}"
                for r in results
            ]
        )
    except Exception as e:
        return f"Web search failed: {e}. Try a narrower query or wait a moment before retrying."


@mcp.tool()
def search_scientific_papers(query: str, max_results: int = 5) -> str:
    """
    Search ArXiv for state-of-the-art scientific papers, preprints, and research.
    """
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
        )
        papers = [
            f"Title: {r.title}\n"
            f"Authors: {', '.join([a.name for a in r.authors])}\n"
            f"Published: {r.published.strftime('%Y-%m-%d')}\n"
            f"PDF URL: {r.pdf_url}\n"
            f"Summary: {r.summary}"
            for r in client.results(search)
        ]
        return "\n\n---\n\n".join(papers)
    except Exception as e:
        return f"ArXiv search failed: {e}"


if __name__ == "__main__":
    mcp.run()
