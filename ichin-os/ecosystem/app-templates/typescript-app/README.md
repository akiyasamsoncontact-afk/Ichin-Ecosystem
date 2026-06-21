# ICHIN OS — TypeScript App Template

A template for building TypeScript apps for the ICHIN OS ecosystem.

## Structure

- `manifest.json` — App manifest with identity, permissions, and AI settings
- `src/index.ts` — Main app entry point with ICHIN OS integration
- `package.json` — Dependencies including `@ichin/sdk` and `@ichin/shared-types`

## Usage

```bash
npm install
npm run build
npm start
```

## Customization

1. Edit `manifest.json` to configure your app
2. Modify `src/index.ts` to implement your app logic
3. Use the `IchinApp` class methods for AI, memory, and notification integration
