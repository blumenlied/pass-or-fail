<script lang="ts">
	import { page } from '$app/stores';
	import {
		CheckPlusCircleSolid,
		ChartMixedOutline,
		BarsOutline,
		HomeOutline,
		ToolsOutline,
		QuestionCircleOutline,
		CloseOutline
	} from 'flowbite-svelte-icons';
	import { onMount, onDestroy } from 'svelte';

	let isOpen = false;

	function toggleSidebar() {
		isOpen = !isOpen;
	}

	let unsubscribeFromPage: () => void;
	onMount(() => {
		unsubscribeFromPage = page.subscribe(() => {
			if (window.innerWidth < 768) {
				isOpen = false;
			}
		});
	});
	onDestroy(() => {
		if (unsubscribeFromPage) unsubscribeFromPage();
	});

	$: currentPath = $page.url.pathname;

	const navLinks = [
		{ href: '/dashboard', label: 'Dashboard', icon: HomeOutline },
		{ href: '/manage', label: 'Management', icon: BarsOutline },
		{ href: '/prediction', label: 'Prediction', icon: ChartMixedOutline }
	];

	const secondaryNavLinks = [
		{ href: '/help', label: 'Help', icon: QuestionCircleOutline }
	];
</script>

<div class="flex bg-gray-100 dark:bg-gray-900">
	<!-- Sidebar -->
	<aside
		id="sidebar"
		aria-label="Main Sidebar"
		class={`fixed inset-y-0 left-0 z-40 w-64 transform bg-white shadow-lg transition-transform duration-300 ease-in-out dark:bg-gray-800
			${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 md:fixed md:block`}
	>
		<div class="flex h-full flex-col">
			<!-- Logo -->
			<div class="p-4">
				<a href="/dashboard" class="group flex items-center space-x-2 text-2xl font-bold text-primary-700 dark:text-primary-400">
					<CheckPlusCircleSolid class="h-8 w-8 transition-transform duration-200 group-hover:rotate-12" />
					<span>Pass or Fail</span>
				</a>
			</div>

			<hr class="mx-4 my-4 border-gray-200 dark:border-gray-600" />

			<!-- Main Nav -->
			<nav class="flex-1 space-y-2 overflow-y-auto p-4">
				{#each navLinks as link}
					<a
						href={link.href}
						class="group flex items-center rounded-lg px-3 py-2.5 text-gray-700 transition-colors duration-200 hover:bg-primary-100 hover:text-primary-700 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
						class:bg-primary-100={currentPath === link.href || (link.href !== '/dashboard' && currentPath.startsWith(link.href))}
						class:text-primary-700={currentPath === link.href || (link.href !== '/dashboard' && currentPath.startsWith(link.href))}
						class:dark:bg-gray-700={currentPath === link.href || (link.href !== '/dashboard' && currentPath.startsWith(link.href))}
						class:dark:text-white={currentPath === link.href || (link.href !== '/dashboard' && currentPath.startsWith(link.href))}
					>
						<svelte:component this={link.icon} class="mr-3 h-5 w-5 flex-shrink-0" />
						<span class="text-sm font-medium">{link.label}</span>
					</a>
				{/each}

				<hr class="mx-1 my-4 border-gray-200 dark:border-gray-600" />

				{#each secondaryNavLinks as link}
					<a
						href={link.href}
						class="group flex items-center rounded-lg px-3 py-2.5 text-gray-700 transition-colors duration-200 hover:bg-primary-100 hover:text-primary-700 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
						class:bg-primary-100={currentPath.startsWith(link.href)}
						class:text-primary-700={currentPath.startsWith(link.href)}
						class:dark:bg-gray-700={currentPath.startsWith(link.href)}
						class:dark:text-white={currentPath.startsWith(link.href)}
					>
						<svelte:component this={link.icon} class="mr-3 h-5 w-5 flex-shrink-0" />
						<span class="text-sm font-medium">{link.label}</span>
					</a>
				{/each}
			</nav>

			<!-- Footer -->
			<div class="mt-auto p-4">
				<form method="POST" action="/logout">
					<button
						type="submit"
						class="w-full rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white transition-colors duration-200 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50"
					>
						Logout
					</button>
				</form>
			</div>
		</div>
	</aside>

	<!-- Main content (pushed right on desktop) -->
	<div class="flex flex-1 flex-col min-h-screen md:pl-64">
		<!-- Mobile top bar -->
		<header class="sticky top-0 z-30 border-b bg-white p-4 shadow-sm md:hidden dark:border-gray-700 dark:bg-gray-800">
			<div class="flex items-center justify-between">
				<a href="/dashboard" class="group flex items-center space-x-2 text-xl font-bold text-primary-700 dark:text-primary-400">
					<CheckPlusCircleSolid class="h-7 w-7" />
					<span>Pass or Fail</span>
				</a>
				<button
					on:click={toggleSidebar}
					aria-label="Toggle sidebar"
					aria-expanded={isOpen}
					aria-controls="sidebar"
					class="rounded-md p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
				>
					{#if isOpen}
						<CloseOutline class="h-6 w-6" />
					{:else}
						<BarsOutline class="h-6 w-6" />
					{/if}
				</button>
			</div>
		</header>

		<main class="flex-1 overflow-y-auto p-6">
			<slot />
		</main>
	</div>

	<!-- Mobile overlay -->
	{#if isOpen}
		<div
			class="fixed inset-0 z-30 bg-black opacity-50 md:hidden"
			on:click={toggleSidebar}
			role="button"
			tabindex="0"
			on:keydown={(e) => e.key === 'Enter' && toggleSidebar()}
		></div>
	{/if}
</div>

