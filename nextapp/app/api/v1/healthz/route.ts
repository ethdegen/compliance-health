import { NextRequest, NextResponse } from "next/server";
import cors from "../../../../src/server/webapi/cors";
import preflight from "../../../../src/server/webapi/cors_preflight";

export async function GET(request: NextRequest) {
    return cors(
        request,
        NextResponse.json({
            up: true,
        }),
        {
            origin: true,
            credentials: true,
        }
    );
}

export async function POST(request: NextRequest) {
    return cors(
        request,
        NextResponse.json({
            up: true,
        }),
        {
            origin: true,
            credentials: true,
        }
    );
}

export { preflight as OPTIONS };
