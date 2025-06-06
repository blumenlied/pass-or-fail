<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let email = '';
	let password = '';
	let error = '';

	async function handleLogin() {
		error = ''; // Clear previous error
		const formData = new FormData();
		// FastAPI's OAuth2PasswordRequestForm expects 'username' for the email field
		formData.append('username', email);
		formData.append('password', password);

		try {
			console.log('Login: Attempting to log in...');
			const res = await fetch('http://localhost:8000/login', {
				method: 'POST',
				body: formData // FastAPI handles FormData for OAuth2PasswordRequestForm
			});

			const responseData = await res.json(); // Try to parse JSON regardless of res.ok for error details

			if (res.ok) {
				console.log('Login: Login successful, token data:', responseData);
				const accessToken = responseData.access_token;

				localStorage.setItem('authToken', accessToken);
				console.log('Login: authToken stored in localStorage.');

				const maxAge = 30 * 60;
				document.cookie = `token=${accessToken}; path=/; SameSite=Lax; Max-Age=${maxAge}`;
				console.log('Login: token cookie set.');

				goto('/dashboard');
			} else {
				error = responseData.detail || 'Invalid email or password';
				console.error('Login: Login failed:', error);
			}
		} catch (err) {
			console.error('Login: Network or other error during login:', err);
			error = 'Login request failed. Please try again.';
		}
	}
</script>

<main class="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-4">
	<div class="w-full max-w-xs rounded-xl bg-white p-6 shadow-lg sm:max-w-sm sm:p-8">
		<h1 class="mb-6 text-center text-2xl font-bold text-gray-700">Faculty Login</h1>

		{#if error}
			<div class="mb-4 rounded-md bg-red-100 p-3 text-center text-sm text-red-700" role="alert">
				{error}
			</div>
		{/if}

		<form on:submit|preventDefault={handleLogin} class="space-y-4">
			<div>
				<label for="email" class="sr-only block text-sm font-medium text-gray-700">Email</label>
				<input
					bind:value={email}
					type="email"
					id="email"
					name="email"
					placeholder="Email address"
					required
					class="input w-full"
				/>
			</div>
			<div>
				<label for="password" class="sr-only block text-sm font-medium text-gray-700"
					>Password</label
				>
				<input
					bind:value={password}
					type="password"
					id="password"
					name="password"
					placeholder="Password"
					required
					class="input w-full"
				/>
			</div>
			<button
				type="submit"
				class="btn w-full rounded-md bg-blue-600 py-2 text-white transition-colors duration-150 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none"
			>
				Login
			</button>
		</form>
	</div>
</main>

<style>
	.input {
		padding: 0.75rem; /* Increased padding */
		border: 1px solid #d1d5db; /* Softer border color */
		border-radius: 0.375rem; /* Consistent with rounded-md */
		box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05); /* Subtle inner shadow */
		transition:
			border-color 0.15s ease-in-out,
			box-shadow 0.15s ease-in-out;
	}
	.input:focus {
		border-color: #3b82f6; /* Blue border on focus */
		outline: none; /* Remove default outline */
		box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25); /* Focus ring */
	}
	.btn {
		padding-top: 0.625rem; /* 10px */
		padding-bottom: 0.625rem; /* 10px */
		font-weight: 600; /* Semibold */
	}
</style>
