import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

function parseId(id: string): number | null {
  const numericId = Number(id);
  return Number.isInteger(numericId) && numericId > 0 ? numericId : null;
}

function extractIdFromRequest(request: Request): number | null {
  const url = new URL(request.url);
  const segments = url.pathname.split("/").filter(Boolean);
  const last = segments[segments.length - 1] ?? "";
  return parseId(last);
}

export async function GET(req: Request) {
  const id = extractIdFromRequest(req);
  if (!id) return NextResponse.json({ error: "Invalid id" }, { status: 400 });
  const task = await prisma.task.findUnique({ where: { id } });
  if (!task) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(task);
}

export async function PATCH(req: Request) {
  const id = extractIdFromRequest(req);
  if (!id) return NextResponse.json({ error: "Invalid id" }, { status: 400 });

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const data: { title?: string; completed?: boolean } = {};
  const b = body as { title?: unknown; completed?: unknown };

  if (typeof b.title === "string") {
    const t = b.title.trim();
    if (t.length === 0) return NextResponse.json({ error: "Title cannot be empty" }, { status: 400 });
    data.title = t;
  }
  if (typeof b.completed === "boolean") {
    data.completed = b.completed;
  }

  if (Object.keys(data).length === 0) {
    return NextResponse.json({ error: "No valid fields to update" }, { status: 400 });
  }

  try {
    const task = await prisma.task.update({ where: { id }, data });
    return NextResponse.json(task);
  } catch {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
}

export async function DELETE(req: Request) {
  const id = extractIdFromRequest(req);
  if (!id) return NextResponse.json({ error: "Invalid id" }, { status: 400 });
  try {
    await prisma.task.delete({ where: { id } });
    return new NextResponse(null, { status: 204 });
  } catch {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
}