const fastify = require("fastify")({
  logger: true,
});

const qrcode = require("qrcode-terminal");
const { Client, LocalAuth } = require("whatsapp-web.js");

const client = new Client({
  authStrategy: new LocalAuth(),
});

//Genera el código qr para conectarse a whatsapp-web
client.on("qr", (qr) => {
  qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
  console.log("whatsapp ready");
});

isWaContact = async (params) => {
  const { phone } = params;
  contact = await client.getNumberId(phone);
  console.log(contact);
  return contact ? true : false;
};

// Declare a route
fastify.get("/", function (_request, reply) {
  reply.send({ message: "service available" });
});

fastify.get("/whatsapp/:phone", async (request, reply) => {
  //   console.log(request);
  //   console.log(request.params);
  console.log("query: ", request.query);
  console.log("value: ", request.query.phone);
  const result = await isWaContact(request.query);
  reply.send({
    message: result ? "is wa contact" : "is not wa contact",
    result: result,
  });
});

// Run the server!
fastify.listen({ port: 5555 }, function (err, address) {
  client.initialize();
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  // Server is now listening on ${address}
});
