# 🛡️ RTrap – Ransomware Detection & Containment using Decoy Files and ML

RTrap is a **Python-based research framework** designed to detect and contain ransomware attacks using **decoy (honeypot) files** and **machine learning clustering**.The system plants realistic fake files in user directories and continuously monitors them. If ransomware touches a decoy, RTrap instantly responds by **killing the malicious process** and **disconnecting the network** to prevent data loss and lateral spread.  

---

## 🚀 Features
- 📂 **Decoy File Generator** – Uses ML (Affinity Propagation clustering) to create realistic honeypot files.  
- 👁️ **Decoy Watcher** – Monitors decoys in real time and triggers alerts on modification.  
- 🔪 **Containment Actions** – Kills malicious processes and disconnects the system from the network.  
- 🧪 **Safe Simulation** – Includes test ransomware scripts for controlled experiments.  
- 🖥️ **Cross-Platform (Prototype)** – Works on Windows (Linux can be adapted).  

---

## 📂 Folder Structure
```
RTrap/
│
├── data/                         # Stores decoy metadata and logs
│   ├── decoy_list.txt            # List of all decoy files
│   └── rtrap_log.txt             # Log file for ransomware events With TimeStamps
│
├── src/                          # Main source code
│   ├── config/                   # Configuration files
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── generator/                # Decoy file generation logic
│   │   ├── __init__.py
│   │   ├── decoy_creator.py
│   │   ├── decoy_picker.py
│   │   ├── feature_extractor.py
│   │   ├── file_attributes_preprocessor.py
│   │   └── generator.py
│   │
│   ├── utils/                    # Utility and helper scripts
│   │   ├── __init__.py
│   │   ├── data_processing.py
│   │   ├── file_utils.py
│   │   └── system_utils.py
│   │
│   └── watcher/                  # Real-time ransomware detection
│       ├── __init__.py
│       ├── actions.py
│       ├── event_handler.py
│       ├── file_monitor.py
│       └── watcher.py
│
├── tests/                        # Future tests folder
│
├── venv/                         # Virtual environment (ignored in Git)
│
├── main.py                       # Main entry point
├── simulate_ransomware.py        # Script to simulate ransomware attack
└── requirements.txt              # Python dependencies

```

---

## ⚙️ Setup & Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/RTrap.git
cd RTrap
```

### 2. Create Virtual Environment
```bash
python -m venv rtrap-env
rtrap-env\Scripts\activate   # Windows
source rtrap-env/bin/activate # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
## Requirements

The following Python packages are required for this project:

- **scikit-learn** – For machine learning clustering algorithms
- **watchdog** – For monitoring file system changes
- **psutil** – For managing and monitoring system processes
- **cryptography** – Used in ransomware simulation and encryption functionalities

---

## 🧑‍💻 Usage

### 1. Generate Decoy Files
```bash
python -m src.main --mode generate --directory "Targated Folder/directory Path"
```
This will create fake but realistic files (e.g., report_backup.docx) in your Test folders.

### 2. Start the Watcher
```bash
python -m src.main --mode watch --directory "Targated Folder/directory Path"
```
RTrap will now monitor all decoys in real-time.
If a ransomware-like process modifies them, you’ll see an alert 🚨 and containment actions will trigger.

### 3. Run Ransomware Simulation
```bash
python simulate_ransomware.py
```
This script simulates a ransomware attack on your Test/ folder.
You’ll see **alerts** and **automatic containment actions** if ransomware attempts to modify a decoy.

---

## 🎥 Demo

- **👇Full Simulation Demo(Decoy-Generate/Decoy-Watch/Ransom-Script)**

👉 [🔗 Watch Full Simulation Demo Video](https://github.com/mannu0359/R/blob/d51ca9e7b5b37a11d0d64a7573b962af14ffee6d/RTrap/Demo%20Videos%20and%20Screeshots/Rtrap.mp4)




- **Decoy Generation👇**

![Watch Demo](https://raw.githubusercontent.com/manvendrasingh108/RTrap-Ransomware-Detection-Containment-using-Decoy-Files-and-ML/refs/heads/master/RTrap/Demo%20Videos%20and%20Screeshots/Generate.png)

- **Decoy Log File Generated(Decoy files-info)👇**

![Watch Demo](https://raw.githubusercontent.com/manvendrasingh108/RTrap-Ransomware-Detection-Containment-using-Decoy-Files-and-ML/refs/heads/master/RTrap/Demo%20Videos%20and%20Screeshots/DecoyLog.jpg)

- **Decoy Watcher👇**

![Watch Demo](https://raw.githubusercontent.com/manvendrasingh108/RTrap-Ransomware-Detection-Containment-using-Decoy-Files-and-ML/refs/heads/master/RTrap/Demo%20Videos%20and%20Screeshots/Watch.png)

- **Ransomware Detected👇**

![Watch Demo](https://raw.githubusercontent.com/manvendrasingh108/RTrap-Ransomware-Detection-Containment-using-Decoy-Files-and-ML/refs/heads/master/RTrap/Demo%20Videos%20and%20Screeshots/Alert.png)

- **Activity/Alert Log File Generated(Alert/Ransomware Detection Alert/File Modified Alert Registered With Timestamps in Alert Log File)👇**

![Watch Demo](https://raw.githubusercontent.com/manvendrasingh108/RTrap-Ransomware-Detection-Containment-using-Decoy-Files-and-ML/refs/heads/master/RTrap/Demo%20Videos%20and%20Screeshots/Activitylog.jpg)

---

## 📊 Workflow
1. **Decoy Generation** → ML clustering chooses representative files → creates honeypots.  
2. **Monitoring** → Watchdog monitors decoys for suspicious changes.  
3. **Detection** → Alert triggered on decoy access.  
4. **Containment** → Process killed & network disabled.  

---

## 🤝 Contributing
Contributions are welcome!  
If you’d like to improve RTrap, add features, or fix bugs, feel free to:  
1. Fork this repository  
2. Create a feature branch  
3. Submit a Pull Request  

Together, we can make this an even better tool for security research. 💡

---

## ⚠️ Disclaimer
This project is strictly for **educational and research purposes only**.  
Do **NOT** run ransomware simulation scripts on real or sensitive data. Always use test files in isolated environments.  


## 📚 References

- [Affinity Propagation (scikit-learn docs)](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AffinityPropagation.html)  
- [Watchdog File Monitoring](https://www.geeksforgeeks.org/create-a-watchdog-in-python-to-look-for-filesystem-changes/)  


---
 
