# LIM Serial - GUI de Comunicación Serial y Visualización de Datos

**README en:** [English](README.md) | [Português](README_pt-br.md) | [Español](README_es.md) | [Deutsch](README_de.md) | [Français](README_fr.md)

---

## Descripción General

LIM Serial es una aplicación GUI moderna e internacionalizada para comunicación serial y visualización de datos en tiempo real. Construida con Python/Tkinter y matplotlib, proporciona una interfaz amigable para conectar a dispositivos seriales, recopilar datos y crear gráficos dinámicos.

![Captura de Pantalla de LIM Serial](shot.png)

## Características

### 🌍 **Internacionalización**
- **5 Idiomas**: Inglés, Portugués (Brasil), Español, Alemán, Francés
- **Cambio en Tiempo Real**: Cambie el idioma sin reiniciar
- **Preferencias Persistentes**: Selección de idioma guardada automáticamente
- **Traducciones en YAML**: Fácil de extender con nuevos idiomas

### 📡 **Comunicación Serial**
- **Modo Hardware**: Conecte a puertos seriales reales
- **Modo Simulado**: Puerto virtual integrado con generación de datos
- **Detección Automática**: Descubrimiento y actualización automática de puertos
- **Baudrate Flexible**: Soporte para todos los baudrates estándar
- **Estado en Tiempo Real**: Información de conexión con retroalimentación visual

### 📊 **Visualización de Datos**
- **Múltiples Tipos de Gráfico**: Línea, Barras, Dispersión
- **Actualizaciones en Tiempo Real**: Graficado de datos en vivo con actualización configurable
- **Apariencia Personalizable**: Más de 20 colores, más de 10 tipos de marcadores
- **Control de Ejes**: Límites manuales del eje Y y ventanas
- **Exportación PNG**: Guarde gráficos como imágenes de alta calidad
- **Pausar/Reanudar**: Controle el flujo de datos sin desconectar

### 💾 **Gestión de Datos**
- **Guardar/Cargar**: Exportar e importar datos en formato texto
- **Guardado Automático**: Respaldo automático de datos con confirmación del usuario
- **Función Limpiar**: Resetear datos con avisos de seguridad
- **Configuraciones Persistentes**: Todas las preferencias guardadas entre sesiones

### 🎨 **Interfaz de Usuario**
- **Interfaz con Pestañas**: Pestañas organizadas de Configuración, Datos y Gráfico
- **Diseño Responsivo**: Diseño adaptativo con dimensionamiento adecuado de widgets
- **Retroalimentación Visual**: Indicadores de estado e información de progreso
- **Accesibilidad**: Etiquetado claro y navegación intuitiva

## Instalación

### Requisitos
- Python 3.7+
- tkinter (usualmente incluido con Python)
- matplotlib
- pyserial
- PyYAML

### Instalar Dependencias
```bash
pip install matplotlib pyserial PyYAML
```

### Inicio Rápido
```bash
# Clone o descargue el proyecto
cd lim_serial

# Ejecute la aplicación
python lim_serial.py
```

## Guía de Uso

### 1. Pestaña de Configuración
- **Selección de Modo**: Elija entre modo Hardware o Simulado
- **Selección de Puerto**: Seleccione entre puertos seriales disponibles (auto-actualizados)
- **Baudrate**: Configure la velocidad de comunicación
- **Conectar/Desconectar**: Establezca o cierre la conexión serial

### 2. Pestaña de Datos
- **Visualización en Tiempo Real**: Vea los datos recibidos en formato tabular
- **Guardar Datos**: Exporte el conjunto de datos actual a archivo de texto
- **Cargar Datos**: Importe datos guardados anteriormente
- **Limpiar Datos**: Resetee el conjunto de datos actual
- **Guardado Automático**: Respaldo automático con confirmación del usuario

### 3. Pestaña de Gráfico
- **Selección de Columnas**: Elija columnas X e Y para graficar
- **Tipos de Gráfico**: Seleccione gráfico de Línea, Barras o Dispersión
- **Personalización**: Colores, marcadores, límites de eje, tamaño de ventana
- **Exportar**: Guarde gráficos como imágenes PNG
- **Pausar/Reanudar**: Controle actualizaciones en tiempo real

### 4. Menú de Idiomas
- **Selección de Idioma**: Disponible en la barra de menú principal
- **Cambio en Tiempo Real**: Los cambios se aplican inmediatamente
- **Persistente**: Preferencia de idioma guardada automáticamente

## Formato de Datos

Los datos seriales deben enviarse en columnas separadas por espacios:

```
# Encabezado (opcional)
timestamp voltage current temperature

# Filas de datos
1.0 3.3 0.125 25.4
2.0 3.2 0.130 25.6
3.0 3.4 0.122 25.2
```

**Características:**
- Valores separados por espacio o tab
- Detección automática de columnas
- Análisis de datos numéricos
- Soporte de fila de encabezado (ignorada durante graficado)

## Arquitectura del Proyecto

### Gestión de Configuración
- **Preferencias del Usuario**: Almacenadas en `config/prefs.yml`
- **Configuraciones Específicas de Pestaña**: Organizadas por sección de la interfaz
- **Persistencia de Idioma**: Memoria automática de selección de idioma
- **Valores Predeterminados Seguros**: Valores de respaldo para todas las preferencias

### Sistema de Traducción
- **Basado en YAML**: Archivos de traducción legibles en `languages/`
- **Claves Jerárquicas**: Organizadas por componente de UI y contexto
- **Soporte de Respaldo**: Las traducciones faltantes vuelven al inglés
- **Actualizaciones en Tiempo Real**: La interfaz se actualiza inmediatamente al cambiar idioma

## Desarrollo

### Agregando Nuevos Idiomas
1. Cree un nuevo archivo YAML en el directorio `languages/`
2. Siga la estructura de los archivos de idioma existentes
3. Pruebe todas las cadenas de la interfaz
4. Envíe una pull request

### Extendiendo Funcionalidad
- **Protocolos Seriales**: Extienda `SerialManager` para protocolos personalizados
- **Tipos de Gráfico**: Agregue nuevos tipos de plot en `GraphManager`
- **Formatos de Datos**: Implemente analizadores personalizados en `utils/`
- **Componentes de UI**: Cree nuevas pestañas siguiendo patrones existentes

## Archivos de Configuración

### Preferencias del Usuario (`config/prefs.yml`)
```yaml
language: es
tabs:
  config:
    mode: Hardware
    port: "/dev/ttyUSB0"
    baudrate: "9600"
  graph:
    type: Line
    color: Blue
    marker: circle
    window_size: "100"
    x_column: "1"
    y_column: "2"
```

### Archivos de Idioma (`languages/*.yml`)
Archivos de traducción estructurados con organización jerárquica por componente de UI.

## Contribuyendo

1. Haga fork del repositorio
2. Cree una rama de funcionalidad
3. Haga sus cambios
4. Pruebe completamente (especialmente internacionalización)
5. Envíe una pull request

### Áreas para Contribución
- Nuevas traducciones de idiomas
- Tipos de gráfico adicionales
- Protocolos seriales mejorados
- Mejoras de UI/UX
- Mejoras de documentación

## Licencia

Desarrollado por CBPF-LIM (Centro Brasileño de Investigaciones Físicas - Laboratorio de Luz y Materia).

## Soporte

Para problemas, solicitudes de funcionalidades o preguntas:
- Verifique la documentación existente
- Revise archivos de traducción para cadenas de UI
- Pruebe con diferentes idiomas y configuraciones
- Reporte errores con pasos detallados de reproducción

---

**LIM Serial** - Comunicación serial moderna simplificada con accesibilidad internacional.
