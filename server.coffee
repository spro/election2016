
polar = require 'somata-socketio'
app = polar port: 5477
app.get '/', (req, res) -> res.render 'index'
app.start()
