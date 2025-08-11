import { deployService } from '@/lib/eioService/eioService.js';

export const dynamic = 'force-dynamic';

export async function POST (request) {
  const config = await request.json();
  const res = await deployService(JSON.stringify(config));

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
  }

  return new Response(JSON.stringify({
    message: msg
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
