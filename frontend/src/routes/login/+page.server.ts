import { redirect } from '@sveltejs/kit';

export const load = async ({ cookies }) => {
	const token = cookies.get('token');
	if (token) {
		throw redirect(302, '/dashboard');
	}
};

