import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
  const token = cookies.get('token');

  if (!token) {
    throw redirect(302, '/login');
  }

  const res = await fetch('http://localhost:8000/students', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!res.ok) {
    throw redirect(302, '/login');
  }

  const students = await res.json();
  return { students };
};


