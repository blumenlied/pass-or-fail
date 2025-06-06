// src/routes/(app)/dashboard/+page.ts
import type { PageLoad } from './$types'; // Import PageLoad for better typing

export const load: PageLoad = async ({ fetch, cookies }) => {
        const token = cookies.get('token'); // Attempt to get the token from cookies
    try {

        if (!token) {
            // This case should ideally be handled by a +layout.server.ts or hooks
            // that redirect to /login if no token is present.
            // For now, we'll throw an error indicating a probable auth issue.
            console.error('Dashboard Load: No token found in cookies.');
            return { // Return an error state that the page can display
                dashboardData: null,
                error: "Authentication token not found. Please log in."
            };
        }

        const response = await fetch('http://localhost:8000/dashboard-stats', {
            headers: {
                'Authorization': `Bearer ${token}` // Include the token in the header
            }
        });

        if (!response.ok) {
            console.error('Fetch error status:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Fetch error details:', errorText);
            // Specific check for 401 Unauthorized
            if (response.status === 401) {
                 return {
                    dashboardData: null,
                    error: `Authentication failed (401): ${errorText || 'Invalid or expired token.'} Please log in again.`
                 };
            }
            throw new Error(`Failed to fetch dashboard data (status: ${response.status})`);
        }
        const dashboardApiResponse = await response.json();

        return {
            dashboardData: dashboardApiResponse,
            error: null // Explicitly set error to null on success
        };

    } catch (error: any) { // Catch with 'any' or 'unknown' and then check type
        console.error("Error loading dashboard data in +page.ts:", error);
        return {
            dashboardData: null,
            error: error.message || "Could not load dashboard information. Please check console."
        };
    }
};
