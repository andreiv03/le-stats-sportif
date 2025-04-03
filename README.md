# Le Stats Sportif

A Flask-based **data processing API** that serves insightful statistics from a sports and nutrition dataset. With support for **parallel processing**, **robust logging**, and **graceful shutdown**, this tool offers fast, scalable endpoints to query and analyze structured data.

## ✨ Features

- **Extensive Statistical Endpoints** – Access national and state-specific means, differences from the average, and category-based statistics.
- **Job Management** – Handle long-running tasks asynchronously using a job queue system.
- **Modular Flask Design** – Clean route separation and a scalable architecture.
- **Graceful Shutdown** – Ensures background jobs and processes are safely terminated on exit.
- **Logging System** – Integrated logger using UTC timestamps and rotating file handlers.
- **CSV Dataset Integration** – Built-in dataset included for immediate use.

## ⚡ Technology Stack

- **Python (3.9 or later)** – Main back-end language.
- **Flask** – Web framework for building RESTful APIs.
- **Pandas** – Used for efficient data manipulation and processing.
- **Multiprocessing** – Manages concurrent jobs for better performance.

## ⚙️ Build & Installation

### Prerequisites

Before installing the project, ensure you have the following installed:

- **Python 3.9+** (for running the Flask application)
- **pip (Python package manager)**

### Installation Instructions

Follow these steps to clone, build, and run the server:

```sh
# Clone the repository
git clone https://github.com/andreiv03/le-stats-sportif.git
cd le-stats-sportif

# Create virtual environment
make create_venv

# Install dependencies
make install

# Run the server
make run_server
```
The app will be accessible at [http://localhost:5000](http://localhost:5000).

## 📂 Dataset

Includes `nutrition_activity_obesity_usa_subset.csv` with pre-cleaned US health data.

## 🤝 Contributing

Contributions are welcome! If you'd like to enhance the project, follow these steps:

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature-branch`)
3. **Commit** your changes (`git commit -m "feat: add new feature"`)
4. **Push** your changes (`git push origin feature-branch`)
5. Open a **Pull Request** 🚀

For suggestions or bug reports, feel free to open an issue with the appropriate label.

⭐ **If you find this project useful, consider giving it a star!** ⭐

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.
