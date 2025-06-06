<!-- src/routes/+page.svelte -->
<script lang="ts">
	import { goto } from '$app/navigation';
	import {
		BrainOutline,
		ChartOutline,
		GraduationCapOutline,
		ArrowRightOutline
	} from 'flowbite-svelte-icons';

	const features = [
		{
			icon: BrainOutline,
			title: 'AI-Powered Predictions',
			description:
				'Leverage advanced machine learning to predict student success in certification exams.'
		},
		{
			icon: ChartOutline,
			title: 'Insightful Dashboard',
			description:
				'Visualize overall student performance and key metrics at a glance for informed decision-making.'
		},
		{
			icon: GraduationCapOutline,
			title: 'Comprehensive Management',
			description:
				'Easily manage student records, track progress, and update information seamlessly.'
		}
	];
</script>

<svelte:head>
	<title>Intelligent Student Performance Predictor</title>
	<meta
		name="description"
		content="Empowering faculty with AI-driven insights to enhance student success in certification exams."
	/>
</svelte:head>

<div
	class="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-sky-50 to-indigo-100 p-4 selection:bg-blue-500 selection:text-white dark:from-slate-900 dark:via-sky-900/50 dark:to-indigo-900/30"
>
	<main class="container mx-auto mt-9 max-w-screen-xl text-center">
		<header class="mb-12 md:mb-16">
			<div
				class="mb-6 inline-flex items-center justify-center rounded-full bg-blue-100 p-3 shadow-md dark:bg-blue-900/50"
			>
				<BrainOutline
					class="h-12 w-12 transform text-blue-600 transition-transform duration-300 hover:scale-110 dark:text-blue-400"
				/>
			</div>
			<h1
				class="mb-4 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl md:text-6xl dark:text-white"
			>
				Intelligent Student <span class="text-blue-600 dark:text-blue-500"
					>Performance Predictor</span
				>
			</h1>
			<p class="mx-auto max-w-xl text-lg text-slate-600 sm:text-xl dark:text-slate-300">
				Empowering faculty with AI-driven insights to enhance student success in certification
				exams.
			</p>
		</header>

		<section class="mb-12 md:mb-16">
			<h2
				class="motion-translate-y-in-100 motion-duration-[2s] motion-ease-spring-smooth mb-8 text-2xl font-semibold text-slate-800 sm:text-3xl md:mb-10 dark:text-slate-100"
			>
				Key Features
			</h2>
			<div
				class="motion-translate-y-in-100 motion-duration-[2s] motion-ease-spring-smooth grid grid-cols-1 gap-6 md:grid-cols-3 md:gap-8"
			>
				{#each features as feature}
					<div
						class="rounded-xl bg-white p-6 shadow-lg backdrop-blur-sm transition-shadow duration-300 hover:shadow-xl dark:bg-slate-800/70"
					>
						<div class="mb-4 flex justify-center">
							<svelte:component
								this={feature.icon}
								class="h-10 w-10 text-blue-500 dark:text-blue-400"
							/>
						</div>
						<h3 class="mb-2 text-lg font-semibold text-slate-900 dark:text-white">
							{feature.title}
						</h3>
						<p class="text-sm text-slate-600 dark:text-slate-300">{feature.description}</p>
					</div>
				{/each}
			</div>
		</section>

		<section class="cta-section">
			<button
				on:click={() => goto('/login')}
				class="mt-4 inline-flex transform items-center justify-center rounded-lg bg-blue-600 px-8 py-3 text-base font-semibold text-white shadow-md transition-all duration-150 ease-in-out hover:scale-105 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 focus:outline-none sm:px-10 sm:py-4 sm:text-lg dark:focus:ring-blue-800"
			>
				Faculty Login
				<ArrowRightOutline class="-mr-1 ml-2 h-5 w-5 sm:h-6 sm:w-6" />
			</button>
			<p class="mt-4 text-sm text-slate-500 dark:text-slate-400">
				Access your dashboard and student management tools.
			</p>
		</section>
	</main>
</div>
