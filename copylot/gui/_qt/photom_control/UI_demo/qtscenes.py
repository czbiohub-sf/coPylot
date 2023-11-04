from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, QApplication
import sys

# Create the application
app = QApplication(sys.argv)

# Create the QGraphicsScene and add a QGraphicsSimpleTextItem to it
scene = QGraphicsScene()
text_item = QGraphicsSimpleTextItem('Hello, world!')
scene.addItem(text_item)

# Create the QGraphicsView and set the scene on it
view = QGraphicsView()
view.setScene(scene)

# Show the view
view.show()

# Run the event loop
sys.exit(app.exec_())