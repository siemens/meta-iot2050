import { retrieveService } from '@/lib/eioService/eioService.js';

export const dynamic = 'force-dynamic';

export async function GET (request) {
  const res = await retrieveService();

  const msg = {
    status: 0,
    message: ''
  };
  if ('code' in res) {
    msg.status = res.code;
    msg.message = res.details;
  } else {
    msg.status = res.status;
    msg.message = res.message;
    msg.yaml_data = res.yaml_data;
  }

  return new Response(JSON.stringify({
    message: msg
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
