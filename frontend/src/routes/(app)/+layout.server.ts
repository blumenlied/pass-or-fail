import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch, url }) => {
	const token = cookies.get('token');

	if (!token) {
		throw redirect(302, '/login');
	}

	// Optionally validate token with your backend
	const res = await fetch(`http://localhost:8000/dashboard`, {
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (!res.ok) {
		throw redirect(302, '/login');
	}

	const dashboardData = await res.json();
	return { dashboardData }; // available in all child pages
};

