# OpenGLViewer
Implementierung eines OpenGL Viewers mit Echtzeit rendering eines eingelesen Objects. 

Im Rahmen einer Abgabe im Modul Generative Computergrafik sollte ein kleiner OpenGL Viewer in Python implementiert werden. 
Das Programm lässt sich via Kommandozeile mit "Renderwindow.py .obj-Filename" starten. Alternativ geht es auch ohne File und 
das Default Bunny wird geladen. 

Dieser ließt .obj-Files ein und berechnet die Normalen der Faces falls keine vorhanden sein sollten. 
Das eingelese Object lässt sich mittels linker Maustaste rotieren. Mit gedrückter mittlerer Maustaste zoomen und mit 
der rechten Maustaste verschieben. 

Desweitern kann der Hintergrund wie auch das Objekt verschiedene Farben annehmen. Auch ein An-/Ausschalten des Objekts ist möglich. 
Ein wechsel zwischen orthograpischer Projektion und perspektivischer Projektion ist möglich. 
