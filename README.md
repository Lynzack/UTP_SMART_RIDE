# UTP Smart Ride 🚗
### AI-Based Carpooling Matching and Route Optimization System

## 1. Project Overview

UTP Smart Ride is an AI-based carpooling system designed to facilitate ride-sharing among Universiti Teknologi PETRONAS (UTP) students. The system aims to reduce the number of individual vehicles travelling to similar destinations by matching passengers with suitable drivers based on their travel schedules, locations, and available seating capacity.

The system integrates **Fuzzy Logic and Genetic Algorithm (GA)** to improve passenger-driver matching and optimize carpooling arrangements. By considering multiple compatibility factors, the system aims to provide efficient ride-sharing arrangements while minimizing additional travel time for drivers.

## 2. Objectives

The main objectives of UTP Smart Ride are:

- To identify suitable driver-passenger matches based on travel requirements.
- To evaluate passenger-driver compatibility using Fuzzy Logic.
- To optimize passenger assignments using a Genetic Algorithm.
- To minimize additional travel time

## 3. System Requirements

Before running UTP Smart Ride, ensure that your system meets the following requirements:

| Requirement | Description |
|---|---|
| Operating System | Windows 10 or Windows 11 |
| Python | Python 3.x |
| pip | Python package manager |
| Web Browser | Google Chrome, Microsoft Edge or Firefox |
| Internet Connection | Required for OSRM routing services and external map resources |

**Note:** Python must be installed and added to the system PATH before running the setup or execution files.

## 8. Installation and Setup

UTP Smart Ride provides an automated setup script to simplify the installation of the required Python dependencies.

### Step 1: Navigate to the Project Directory

Open the project folder after downloading or extracting the project files.

### Step 2: Install Dependencies

Locate and execute `setup.py` by double-clicking the file or running the following command in the terminal:

```bash
python setup.py
```

The setup script automatically installs all required Python libraries listed in `requirements.txt`.

Once the installation is completed, the following message will appear:

```text
All dependencies installed successfully!
```

### Step 3: Run the System

After installing the dependencies, locate and double-click `run.bat` to start the UTP Smart Ride system.

Alternatively, execute the following command in the terminal:

```bash
.\run.bat
```

The batch file automatically:
1. Activates the existing virtual environment if available.
2. Checks whether Flask is installed.
3. Installs the project requirements if Flask is not detected.
4. Starts the backend web server using `backend/server.py`.

### Step 4: Access the Web Application

Once the backend server has started successfully, open a web browser and access the application using the local URL displayed in the terminal.

Keep the terminal window open while using the application. Closing the terminal will stop the backend server..\
