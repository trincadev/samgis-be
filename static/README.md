# ml-tornidor

## Local development

Since I use Cloudflare pages as hosting for this project there are some required steps to do before it's possible to start a local development environment. This project needs to wrap the node commands with the `npx wrangler [...]` utility to emulate a Cloudflare Worker function. Because this worker function is under auth which use some env variables I to write these env variables inline. Every time I changed or added needed some variables I also needed to update the `npx wrangler` command. To avoid this I prepared a js script, executed by [Deno](https://deno.land/), that read the env variables from the `.env` file composing the command:

1. prepare the .env file copying the template.env file
2. run the local environment using the command `pnpm dev` or `deno run -A runner.js`

In case of new or updated packages Deno installs the dependencies at the first execution. Do it with a execution  without the `npx wrangler` wrapper:

```bash
deno run -A --node-modules-dir npm:vite
```

In case of problem:

1. try executing again the command `deno run -A --node-modules-dir npm:vite`

If this don't solve the problems try to

1. delete the node_modules folder
2. reinstall the npm packages with `pnpm install`
3. Run again the local development server, this time with the standard command

Before to commit try also to build using

```bash
pnpm build
```

Then run the preview (change the example variables):

```bash
npx wrangler pages dev --binding VITE_AUTH0_DOMAIN="example-auth0.eu.auth0.com" API_URL="https://example-aws.execute-api.eu-west-1.amazonaws.com/localhost/lambda-ml-fastsam-api" VITE_AUTH0_AUDIENCE="http://localhost-ml-lambda/" API_DOMAIN=example-aws.execute-api.eu-west-1.amazonaws.com CORS_ALLOWED_DOMAIN=http://localhost:8788 VITE_SATELLITE_NAME="tile-provider.image-type" -- pnpm preview
```
