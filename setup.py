"""
Antishitcode 安装配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="antishitcode",
    version="0.1.0",
    description="🧱 Antishitcode - 代码考古学家，让 AI 帮你理解、测试、重构屎山代码",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Antishitcode Team",
    author_email="contact@antishitcode.dev",
    url="https://github.com/antishitcode/antishitcode",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "astor>=0.8.1",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=0.950",
        ],
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "antishitcode=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
