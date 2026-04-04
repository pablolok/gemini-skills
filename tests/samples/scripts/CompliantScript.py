import logging
from pathlib import Path

# Configure logging according to Rule 8
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_file(file_path: str) -> None:
    """
    A compliant function demonstrating platform-agnostic file path handling (Rule 2).
    """
    # COMPLIANT: Pathlib handles cross-platform paths
    base_path = Path("C:/data/files" if Path("C:/").exists() else "/data/files")
    target_file = base_path / file_path
    
    logger.info(f"Processing compliant path: {target_file}")
    
    if target_file.exists():
        logger.info("File exists.")
    else:
        logger.warning("File not found.")

if __name__ == "__main__":
    process_file("sample.txt")
