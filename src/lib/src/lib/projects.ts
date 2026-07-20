import { apiFetch } from "./api";

export type Project = {
  id: string;
  title: string;
  description?: string;
};

export async function getProjects() {
  return apiFetch<Project[]>("/projects");
}