"""GitHub API integration for Modal examples."""

import asyncio
import base64
from pathlib import Path

import httpx
from loguru import logger


class GitHubAPI:
    """Async GitHub API client for Modal examples."""

    BASE_URL = "https://api.github.com"
    REPO_OWNER = "modal-labs"
    REPO_NAME = "modal-examples"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_repo_contents(self, path: str = "") -> list[dict[str, any]]:
        """Get repository contents for a specific path."""
        url = f"{self.BASE_URL}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/{path}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch repo contents for path '{path}': {e}")
            return []

    async def get_file_content(self, path: str) -> str:
        """Get the content of a specific file."""
        url = f"{self.BASE_URL}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/{path}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
            else:
                return data.get("content", "")

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch file content for '{path}': {e}")
            return ""

    async def get_all_folders(self) -> list[dict[str, str]]:
        """Get all folders in the repository root."""
        contents = await self.get_repo_contents()

        folders = []
        for item in contents:
            if item.get("type") == "dir":
                folders.append({
                    "name": item["name"],
                    "path": item["path"]
                })

        return sorted(folders, key=lambda x: x["name"])

    async def get_python_files_in_folder(self, folder_path: str) -> list[dict[str, str]]:
        """Get all Python files in a specific folder."""
        contents = await self.get_repo_contents(folder_path)

        python_files = []
        for item in contents:
            if item.get("type") == "file" and item["name"].endswith(".py"):
                python_files.append({
                    "name": item["name"],
                    "path": item["path"]
                })

        return sorted(python_files, key=lambda x: x["name"])

    async def get_readme_content(self, folder_path: str = "") -> str:
        """Get README.md content for a folder, with fallback to root README."""
        # Try folder-specific README first
        if folder_path:
            readme_path = f"{folder_path}/README.md"
            content = await self.get_file_content(readme_path)
            if content:
                return content

        # Fallback to root README
        root_readme_content = await self.get_file_content("README.md")
        return root_readme_content

    async def search_files_by_extension(self, extension: str, folder_path: str = "") -> list[dict[str, str]]:
        """Search for files with specific extension in a folder."""
        contents = await self.get_repo_contents(folder_path)

        files = []
        for item in contents:
            if item.get("type") == "file" and item["name"].endswith(extension):
                files.append({
                    "name": item["name"],
                    "path": item["path"]
                })
            elif item.get("type") == "dir" and folder_path == "":
                # Recursively search in subdirectories (only one level deep for performance)
                subfolder_files = await self.search_files_by_extension(extension, item["path"])
                files.extend(subfolder_files)

        return sorted(files, key=lambda x: x["name"])


# Global GitHub API instance
github_api = GitHubAPI()
