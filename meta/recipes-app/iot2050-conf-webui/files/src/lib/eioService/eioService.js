import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';
const PROTO_PATH = path.join(__dirname, '../gRPC/iot2050-eio.proto');

const deployPromise = function (client, yamlStr) {
  return new Promise((resolve, reject) => {
    client.Deploy({ yaml_data: yamlStr }, (err, DeployReply) => {
      if (err) reject(err);
      else resolve(DeployReply);
    });
  });
};

const retrievePromise = function (client) {
  return new Promise((resolve, reject) => {
    client.Retrieve({}, (err, retrieveReply) => {
      if (err) reject(err);
      else resolve(retrieveReply);
    });
  });
};

export async function deployService (yamlStr) {
  const packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
      keepCase: true,
      longs: String,
      enums: String,
      defaults: true,
      oneofs: true
    });
  const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
  const eiomanager = protoDescriptor.eiomanager;
  const client = new eiomanager.EIOManager('localhost:5020',
    grpc.credentials.createInsecure());

  let res;
  try {
    res = await deployPromise(client, yamlStr);
  } catch (err) {
    res = err;
  }

  return res;
};

export async function retrieveService () {
  const packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
      keepCase: true,
      longs: String,
      enums: String,
      defaults: true,
      oneofs: true
    });
  const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
  const eiomanager = protoDescriptor.eiomanager;
  const client = new eiomanager.EIOManager('localhost:5020',
    grpc.credentials.createInsecure());

  let res;
  try {
    res = await retrievePromise(client);
  } catch (err) {
    res = err;
  }

  return res;
};
