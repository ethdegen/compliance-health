## Hackathon template

This template is intended for experimenting with agentic AI applications. 
It permits starting simple yet with ample room to grow to production grade.

### FastAPI structure

The FastAPI server is in `/fastapi`. Its goal is to implement and expose the 
primary backend of the application including LangChains via LangServe and/or 
LlamaIndex and/or HuggingFaces. If beneficial, this FastAPI server can also 
host secondary frontends such as Streamlit implementations for data analysis. 

The Prisma Project is owned by the FastAPI server. Prisma Migrations must be 
deployed along with the FastAPI server and the Prisma Schema resides within it. 
However, for expediency, the Next App is _also_ able to read and write the 
database via Prisma Models generated in TypeScript within the Next App.

The FastAPI server has this folder structure:

```txt {6-10,14-15}
fastapi
├── prisma (Prisma ORM Project)
│   ├── schema.prisma (Prisma DB Schema)
│   └── ...
├── src (Backend-focused Sources)
│   ├── app.py
│   └── ...
├── tests (Unit & Integration Tests)
│   ├── utils.ts (ShadCN UI Utilities)
│   └── ...
└── pyproject.toml
```

### Next App structure

The Next.js App is in `/nextapp`. Its goal is to implement and expose the 
primary frontend of the application as well as any backends-for-frontend 
and/or secondary backends, such as NextAuth, where implementing them as part 
of the Next App streamlines and accelerates development versus alternatives.

To help kickstart application development, the ShadCN UI CLI has been pre-configured.

For expediency, the Next App is able to read and write the database via generated 
Prisma Models although it does _not_ own the Prisma Project. This provision permits
permit packages such as NextAuth to be adopted in an expedient fashion, by sharing 
the pre-existing Prisma Project and database setup owned by the FastAPI server.

The Next App has this folder structure:

```txt {6-10,14-15}
nextapp
├── app (App Router)
│   ├── layout.tsx
│   ├── page.tsx
│   └── ...
├── components (React Components)
│   ├── ui (ShadCN UI Components)
│   │   └── ...
│   └── ...
├── lib (Frontend-focused Libraries)
│   ├── utils.ts (ShadCN UI Utilities)
│   └── ...
├── public (Public-facing Assets)
│   ├── favicon.ico (Favicon Branding)
│   └── ...
├── src (Backend-focused Sources)
│   ├── server (Server-side Sources)
│   |   ├── webapi (WebAPI-related Sources)
│   │   └── ...
│   └── ...
├── styles (CSS-Related Stuff)
│   ├── globals.css (CSS Globals)
│   └── ...
├── next.config.mjs
├── package.json
├── postcss.config.js
├── tailwind.config.js
└── tsconfig.json
```
