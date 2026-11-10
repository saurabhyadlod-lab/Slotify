# 🅿️ SmartPark — Smart Parking Management System

A beginner-friendly Python parking management project with a clean Streamlit dashboard.

## Problem statement
In small parking facilities, drivers and attendants may waste time finding free spaces. Manual tracking can cause duplicate allocations, unclear availability and billing mistakes.

## Our solution
SmartPark keeps a digital record of parking spaces and vehicle movements. It automatically assigns an available space, prevents duplicate active vehicle entries, calculates a parking fee and saves the parking history.

## Features
- Dashboard with total, available and occupied spaces
- Visual parking map (green = available, red = occupied)
- Automatic allocation of the first free slot
- Duplicate vehicle check
- Vehicle checkout and fee calculation (₹20/hour)
- Parking history saved locally
- Downloadable parking history

## Built with
- Python
- Streamlit
- JSON file storage
- Object-oriented programming (`class`, inheritance, abstract class)

## Run locally
1. Install Python 3.
2. Open a terminal in this folder.
3. Install Streamlit:

   ```bash
   pip install streamlit
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown in the terminal.

## How to use
1. Open **Vehicle Entry / Exit**.
2. Enter a vehicle registration number and assign a parking slot.
3. For checkout, select the parked vehicle and enter the parking duration.
4. View the visual layout on **Dashboard**.
5. Open **Parking History** to review or download records.

## Project scope and limitations
This is a software simulation for an academic project. It does not connect to physical sensors, cameras, GPS, gates or online payments. Parking duration is entered manually during checkout. Data is stored in a local JSON file (`parking_data.json`).

## Future scope
- Automatic duration calculation from timestamps
- User accounts and admin login
- Advance slot booking
- Sensor or camera integration
- Online payment integration
