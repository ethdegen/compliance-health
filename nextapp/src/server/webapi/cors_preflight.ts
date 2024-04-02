import cors from "./cors";

export default async function preflight(req: Request) {
    return await cors(
        req,
        new Response(null, {
            status: 204,
        }),
        corsOptions()
    );
}

export function corsOptions() {
    return {
        origin: true,
        credentials: true,
        allowedHeaders: ["Content-Type", "Authorization", "x-promptcmsai-executionid", "x-promptcmsai-semver"],
        exposedHeaders: ["Content-Range", "x-promptcmsai-executionid", "x-promptcmsai-semver"],
    };
}
