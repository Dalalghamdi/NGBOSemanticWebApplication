# Next Generation Biobanking Semantic Web Application

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

This repository provides an open-source **semantic web application** for **federated querying and integration of omics-derived biobank data** across distributed repositories.

Developed as part of the doctoral thesis:

> *Introduction of Omics Metadata into Biobanking Ontology*  

---

## ✨ Overview

Traditional biobank data systems are siloed, making it difficult for researchers to **find, access, and integrate specimen-related data** scattered across institutions. Centralized data warehouses can be costly, slow to update, and may conflict with data governance policies.

This application offers a **federated querying approach** using Semantic Web technologies, enabling:

- Real-time queries over multiple biobank SPARQL endpoints
- No need to centralize or duplicate data
- Support for **FAIR Data Principles** (Findable, Accessible, Interoperable, Reusable)
- Fine-grained, ontology-driven access control
- User-friendly web interface for researchers and data managers

---

## 💡 Features

✅ Federated querying across distributed RDF datasets  
✅ NGBO-aligned semantic integration  
✅ Excel/JSON-based data mapping templates  
✅ Role-based access control and user authentication  
✅ Interactive query results visualization  
✅ Specimen request workflow  
✅ Flexible API-based architecture

---



## 🛠 Installation

### Prerequisites

- Python 3.8+
- GraphDB or other RDF triple store
- Node.js (optional, for front-end build)
- Docker (optional)

---

### Quick Start (Local)

1. **Clone the repository:**

```bash
git clone https://github.com/Dalalghamdi/NGBOSemanticWebApplication.git
cd NGBOSemanticWebApplication
```

2. **Create a virtual environment and install dependencies:**
  
  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
3. **Configure environment variables:**

  ```bash
  GRAPHDB_ENDPOINT=https://your-graphdb-endpoint/repositories/biobank
  SECRET_KEY=your-secret-key
  ```

4. **Run the application:**

```
python backend/app.py
```
Open in browser:
```
http://localhost:5000
```

---
🤝 Contributing
Contributions are welcome!

Fork the repository
Create a feature branch
Submit a pull request

or please open an issue first to discuss your ideas.


