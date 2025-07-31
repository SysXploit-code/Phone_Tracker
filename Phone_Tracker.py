#!/usr/bin/python
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QComboBox, QTabWidget, QMessageBox, QStyle)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
import pycountry
import requests
import json
import webbrowser
from datetime import datetime

class PhoneInfoWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, phone_number, default_region):
        super().__init__()
        self.phone_number = phone_number
        self.default_region = default_region

    def run(self):
        try:
            parsed_number = phonenumbers.parse(self.phone_number, self.default_region)
            
            # Basic info
            region_code = phonenumbers.region_code_for_number(parsed_number)
            jenis_provider = carrier.name_for_number(parsed_number, "en")
            location = geocoder.description_for_number(parsed_number, "en")
            is_valid_number = phonenumbers.is_valid_number(parsed_number)
            is_possible_number = phonenumbers.is_possible_number(parsed_number)
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            formatted_number_for_mobile = phonenumbers.format_number_for_mobile_dialing(
                parsed_number, self.default_region, with_formatting=True)
            number_type = phonenumbers.number_type(parsed_number)
            timezones = timezone.time_zones_for_number(parsed_number)
            timezoneF = ', '.join(timezones)
            
            # Additional info
            country = pycountry.countries.get(alpha_2=region_code) if region_code else None
            country_name = country.name if country else "Unknown"
            country_flag = f"https://flagcdn.com/w40/{region_code.lower()}.png" if region_code else ""
            
            # Number type description
            type_desc = "Mobile" if number_type == phonenumbers.PhoneNumberType.MOBILE else \
                       "Fixed-line" if number_type == phonenumbers.PhoneNumberType.FIXED_LINE else \
                       "VoIP" if number_type == phonenumbers.PhoneNumberType.VOIP else \
                       "Toll-free" if number_type == phonenumbers.PhoneNumberType.TOLL_FREE else \
                       "Premium rate" if number_type == phonenumbers.PhoneNumberType.PREMIUM_RATE else \
                       "Shared cost" if number_type == phonenumbers.PhoneNumberType.SHARED_COST else \
                       "Personal" if number_type == phonenumbers.PhoneNumberType.PERSONAL_NUMBER else \
                       "Pager" if number_type == phonenumbers.PhoneNumberType.PAGER else \
                       "UAN" if number_type == phonenumbers.PhoneNumberType.UAN else \
                       "Unknown"
            
            # Prepare result dictionary
            result = {
                'phone_number': self.phone_number,
                'location': location,
                'country_name': country_name,
                'country_flag': country_flag,
                'region_code': region_code,
                'timezone': timezoneF,
                'operator': jenis_provider,
                'valid_number': is_valid_number,
                'possible_number': is_possible_number,
                'international_format': formatted_number,
                'mobile_format': formatted_number_for_mobile,
                'original_number': parsed_number.national_number,
                'e164_format': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                'country_code': parsed_number.country_code,
                'local_number': parsed_number.national_number,
                'number_type': type_desc,
                'carrier_info': jenis_provider,
                'current_time': self.get_current_time_in_timezone(timezones[0] if timezones else None),
                'coordinates': self.get_coordinates(location)
            }
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))

    def get_current_time_in_timezone(self, tz):
        if not tz:
            return "Unknown"
        try:
            from pytz import timezone as tz_obj
            from datetime import datetime
            tz = tz_obj(tz)
            return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Unknown"

    def get_coordinates(self, location):
        if not location:
            return None
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="phone_tracker")
            location = geolocator.geocode(location)
            if location:
                return (location.latitude, location.longitude)
        except:
            return None

class PhoneTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SysXploit Phone Tracker")
        self.setWindowIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)))
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("SysXploit Phone Number Tracker")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(header)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.country_combo = QComboBox()
        self.country_combo.setPlaceholderText("Select country code")
        self.populate_country_codes()
        input_layout.addWidget(self.country_combo)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number (without country code)")
        input_layout.addWidget(self.phone_input)
        
        self.track_button = QPushButton("Track Number")
        self.track_button.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        self.track_button.clicked.connect(self.track_phone_number)
        input_layout.addWidget(self.track_button)
        
        main_layout.addLayout(input_layout)
        
        # Tab widget for results
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Basic Info Tab
        self.basic_info_tab = QWidget()
        self.basic_info_layout = QVBoxLayout(self.basic_info_tab)
        
        self.country_flag_label = QLabel()
        self.country_flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.basic_info_layout.addWidget(self.country_flag_label)
        
        self.basic_info_text = QTextEdit()
        self.basic_info_text.setReadOnly(True)
        self.basic_info_text.setStyleSheet("font-family: monospace;")
        self.basic_info_layout.addWidget(self.basic_info_text)
        
        self.tabs.addTab(self.basic_info_tab, "Basic Info")
        
        # Advanced Info Tab
        self.advanced_info_tab = QWidget()
        self.advanced_info_layout = QVBoxLayout(self.advanced_info_tab)
        
        self.advanced_info_text = QTextEdit()
        self.advanced_info_text.setReadOnly(True)
        self.advanced_info_text.setStyleSheet("font-family: monospace;")
        self.advanced_info_layout.addWidget(self.advanced_info_text)
        
        self.map_button = QPushButton("View on Map")
        self.map_button.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px;")
        self.map_button.clicked.connect(self.open_map)
        self.map_button.setEnabled(False)
        self.advanced_info_layout.addWidget(self.map_button)
        
        self.tabs.addTab(self.advanced_info_tab, "Advanced Info")
        
        # Status bar
        self.status_bar = self.statusBar()
        
        # Initialize variables
        self.current_coordinates = None
        
    def populate_country_codes(self):
        countries = phonenumbers.COUNTRY_CODE_TO_REGION_CODE
        country_list = []
        
        for code, regions in countries.items():
            if regions:
                country = pycountry.countries.get(alpha_2=regions[0])
                if country:
                    country_list.append((f"+{code}", country.name))
        
        # Sort by country name
        country_list.sort(key=lambda x: x[1])
        
        for code, name in country_list:
            self.country_combo.addItem(f"{name} ({code})", code)
    
    def track_phone_number(self):
        country_code = self.country_combo.currentData()
        phone_number = self.phone_input.text().strip()
        
        if not phone_number:
            QMessageBox.warning(self, "Input Error", "Please enter a phone number")
            return
            
        full_number = f"{country_code}{phone_number}"
        
        self.status_bar.showMessage("Processing... Please wait")
        self.track_button.setEnabled(False)
        
        self.worker = PhoneInfoWorker(full_number, self.country_combo.currentData()[1:])
        self.worker.finished.connect(self.display_results)
        self.worker.error.connect(self.show_error)
        self.worker.start()
    
    def display_results(self, results):
        self.track_button.setEnabled(True)
        self.status_bar.showMessage("Ready")
        
        # Display country flag if available
        if results['country_flag']:
            try:
                response = requests.get(results['country_flag'])
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.country_flag_label.setPixmap(pixmap.scaled(60, 40, Qt.AspectRatioMode.KeepAspectRatio))
            except:
                self.country_flag_label.setText(f"Flag of {results['country_name']}")
        
        # Basic info tab
        basic_info = f"""
        ========== PHONE NUMBER INFORMATION ==========
        
        Phone Number: {results['phone_number']}
        Location: {results['location']}
        Country: {results['country_name']}
        Region Code: {results['region_code']}
        Timezone: {results['timezone']}
        Current Time: {results['current_time']}
        Operator: {results['operator']}
        Valid Number: {'Yes' if results['valid_number'] else 'No'}
        Possible Number: {'Yes' if results['possible_number'] else 'No'}
        Number Type: {results['number_type']}
        """
        
        self.basic_info_text.setPlainText(basic_info)
        
        # Advanced info tab
        advanced_info = f"""
        ========== TECHNICAL DETAILS ==========
        
        International Format: {results['international_format']}
        Mobile Dialing Format: {results['mobile_format']}
        E.164 Format: {results['e164_format']}
        Original Number: {results['original_number']}
        Country Code: +{results['country_code']}
        Local Number: {results['local_number']}
        
        ========== CARRIER INFORMATION ==========
        
        Carrier: {results['carrier_info'] or 'Unknown'}
        
        ========== LOCATION DATA ==========
        
        Coordinates: {results['coordinates'] or 'Unknown'}
        """
        
        self.advanced_info_text.setPlainText(advanced_info)
        
        # Enable map button if coordinates are available
        self.current_coordinates = results['coordinates']
        self.map_button.setEnabled(self.current_coordinates is not None)
        
        # Show success message
        QMessageBox.information(self, "Success", "Phone number information retrieved successfully!")
    
    def open_map(self):
        if self.current_coordinates:
            lat, lon = self.current_coordinates
            url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}"
            webbrowser.open(url)
    
    def show_error(self, error_msg):
        self.track_button.setEnabled(True)
        self.status_bar.showMessage("Error occurred")
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = PhoneTrackerApp()
    window.show()
    
    sys.exit(app.exec())