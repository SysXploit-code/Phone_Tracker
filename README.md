
# 📱 SysXploit Phone Tracker

Una herramienta de rastreo e identificación de números telefónicos desarrollada con Python y PyQt6. Esta app permite obtener información detallada de un número: país, operador, zona horaria, tipo de línea, formato internacional y más. También muestra su localización estimada en un mapa.

---

## 🧠 Características

- Verificación de números válidos y posibles
- Información del país, zona horaria y operador
- Detección del tipo de número (móvil, fijo, VoIP, etc.)
- Visualización de la ubicación aproximada en OpenStreetMap
- Interfaz gráfica moderna con PyQt6
- Icono de bandera del país correspondiente

---

## 📦 Requisitos

- Python 3.9 o superior

### 📚 Librerías necesarias

```bash
pip install pyqt6 phonenumbers pycountry requests geopy pytz
```

---

## 🚀 Ejecución

```bash
python3 Phone_Tracker.py
```

---

## 📍 Captura de pantalla

<p align="center">
  <img src="https://i.imgur.com/WgcyHNX.png" alt="Captura de pantalla" width="600"/>
</p>

---

## 🌐 Mapa

La app permite abrir la ubicación estimada del número en el navegador usando [OpenStreetMap](https://www.openstreetmap.org).

---

## ⚠️ Advertencia

Esta herramienta **no obtiene la ubicación en tiempo real** de un número. Solo utiliza datos públicos y aproximaciones geográficas según la numeración telefónica. **No se trata de espionaje ni rastreo en vivo.**

---

## 🛡️ Licencia

Este proyecto es de uso libre y educativo. Puedes modificarlo y compartirlo bajo los términos de la licencia MIT.

---

## ✍️ Autor

Desarrollado por [SysXploit-code].  
Sígueme en GitHub: [https://github.com/SysXploit-code](https://github.com/SysXploit-code)
