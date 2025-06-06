// src/routes/(app)/prediction/+page.server.js
import { redirect, error as skError } from '@sveltejs/kit'; // Import error from @sveltejs/kit
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
  const token = cookies.get('token');

  if (!token) {
    console.log('+page.server.js: No token found, redirecting to login.');
    throw redirect(302, '/login');
  }

  console.log('+page.server.js: Token found, fetching initial student data...');

  try {
    const studentsRes = await fetch('http://localhost:8000/students', { // Fetch all students
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!studentsRes.ok) {
      console.error('+page.server.js: Fetch students failed, status:', studentsRes.status);
      if (studentsRes.status === 401) { // Unauthorized
        cookies.delete('token', { path: '/' }); // Clear potentially invalid token
        throw redirect(302, '/login?message=Session expired or invalid. Please log in again.');
      }
      throw skError(studentsRes.status, `Failed to load student data: ${studentsRes.statusText}`);
    }

    const studentsData = await studentsRes.json();
    console.log('+page.server.js: Students data fetched successfully:', studentsData.length);

    return {
      students: studentsData || [], // Ensure it's an array, even if API returns null for empty
    };

  } catch (err) {
    console.error('+page.server.js: Error in load function:', err);
    if (err.status && err.body) { // If it's a SvelteKit error, rethrow
      throw err;
    }
    throw redirect(302, '/login?message=Error loading prediction page data.');
  }
}
