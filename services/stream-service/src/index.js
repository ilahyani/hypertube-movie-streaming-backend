const express = require('express')
const swaggerUi = require('swagger-ui-express')
const swaggerSpec = require('./swagger/swagger')

app = express()

app.get('/api/stream', (req, res) => {
    return res.json({'message': `stream service is up! ${req.headers['x-user-id']}`})
})

app.use(express.json())

const swaggerUiAssetPath = require('swagger-ui-dist').getAbsoluteFSPath()
app.use("/api/stream/docs/swagger-ui", express.static(swaggerUiAssetPath));

app.use('/api/stream/comments', require('./routers/comments'))
app.use('/api/stream/search', require('./routers/search'))
app.use('/api/stream/video', require('./routers/video'))

const swaggerOptions = {
  swaggerOptions: {
    url: "/api/stream/openapi.json",
  },
  customCssUrl: "/api/stream/docs/swagger-ui/swagger-ui.css",
  customJs: [
    "/api/stream/docs/swagger-ui/swagger-ui-bundle.js",
    "/api/stream/docs/swagger-ui/swagger-ui-standalone-preset.js",
    "/api/stream/docs/swagger-ui/swagger-ui-init.js",
  ],
};

app.use(
  "/api/stream/docs",
  swaggerUi.serve,
  swaggerUi.setup(swaggerSpec, swaggerOptions)
);


process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

app.listen(process.env.PORT, () => {
    console.log(`stream service running on port ${process.env.PORT}`)
})
