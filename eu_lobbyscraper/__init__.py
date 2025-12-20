"""
EU Better Regulation Portal - Feedback Downloader

A Python package for downloading and converting public consultation feedback
from the EU Better Regulation Portal.
"""

__version__ = "1.0.0"
__author__ = "EU Lobbyscraper Contributors"
__license__ = "MIT"

from .downloader import EUFeedbackDownloader
from .converter import DocumentConverter
from .batch_converter import AttachmentMarkdownConverter

__all__ = [
    "EUFeedbackDownloader",
    "DocumentConverter",
    "AttachmentMarkdownConverter",
]
