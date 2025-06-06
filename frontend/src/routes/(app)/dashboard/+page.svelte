<script lang="ts">
	import Header from '../Header.svelte';
	import { Alert, Card, Chart } from 'flowbite-svelte';

	export let data;

	let pieChartOptions: any = null;
	let columnChartOptions: any = null;

	const pieColors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899', '#6B7280'];
	const barColor = '#3B82F6';

	function getThemeAwareChartColors() {
		let isDark = false;
		if (typeof document !== 'undefined') {
			isDark = document.documentElement.classList.contains('dark');
		}
		return {
			foreColor: isDark ? '#E5E7EB' : '#374151', // text-gray-200 dark / text-gray-700 light
			gridBorderColor: isDark ? '#374151' : '#E5E7EB', // border-gray-700 dark / border-gray-200 light
			pieStrokeColor: isDark ? '#1F2937' : '#FFFFFF', // bg-gray-800 dark / bg-white light
			tooltipTheme: isDark ? 'dark' : 'light'
		};
	}

	$: if (data?.dashboardData?.data) {
		const { students_per_program, average_score_per_program } = data.dashboardData.data;
		const themeColors = getThemeAwareChartColors(); // Get theme colors

		if (students_per_program && students_per_program.length > 0) {
			pieChartOptions = {
				series: students_per_program.map((p) => p.count),
				labels: students_per_program.map((p) => p.program),
				colors: pieColors.slice(0, students_per_program.length),
				chart: {
					type: 'pie' as const,
					height: 320,
					toolbar: { show: false },
					foreColor: themeColors.foreColor
				},
				stroke: {
					colors: [themeColors.pieStrokeColor],
					width: 2
				},
				dataLabels: {
					enabled: true,
					formatter: (val: number) => `${val.toFixed(1)}%`,
					style: { fontSize: '12px', fontFamily: 'Inter, sans-serif' },
					dropShadow: { enabled: true, top: 1, left: 1, blur: 1, opacity: 0.45 }
				},
				legend: {
					position: 'bottom' as const,
					fontFamily: 'Inter, sans-serif',
					offsetY: 5,
					labels: { colors: themeColors.foreColor }, // Use foreColor for legend labels too
					itemMargin: { horizontal: 10, vertical: 2 }
				},
				tooltip: {
					y: {
						formatter: (val: number, { series, seriesIndex, dataPointIndex, w }: any) => {
							const label = w.globals.labels[seriesIndex];
							return `${label}: ${series[seriesIndex]}`;
						}
					},
					theme: themeColors.tooltipTheme
				}
			};
		} else {
			pieChartOptions = null;
		}

		if (average_score_per_program && average_score_per_program.length > 0) {
			columnChartOptions = {
				series: [
					{
						name: 'Avg Score',
						data: average_score_per_program.map((p) => ({
							x: p.program,
							y: parseFloat(p.average_score?.toFixed(1) || '0')
						})),
						color: barColor
					}
				],
				chart: {
					type: 'bar' as const,
					height: 320,
					fontFamily: 'Inter, sans-serif',
					toolbar: { show: false },
					foreColor: themeColors.foreColor
				},
				plotOptions: {
					bar: {
						columnWidth: average_score_per_program.length > 5 ? '70%' : '45%',
						borderRadius: 6,
						dataLabels: { position: 'top' }
					}
				},
				dataLabels: {
					enabled: true,
					formatter: (val: number) => val.toFixed(1),
					offsetY: -20,
					style: { fontSize: '12px', colors: [themeColors.foreColor] }
				},
				xaxis: {
					type: 'category' as const,
					labels: {
						style: {
							fontFamily: 'Inter, sans-serif'
							// For direct styling, cssClass is better if you have global CSS for it.
							// Here, we rely on chart's foreColor for basic theming.
						},
						rotate: average_score_per_program.length > 6 ? -45 : 0,
						rotateAlways: average_score_per_program.length > 6
					},
					axisBorder: { show: false },
					axisTicks: { show: false }
				},
				yaxis: {
					labels: {
						formatter: (val: number) => val.toFixed(0),
						style: {
							fontFamily: 'Inter, sans-serif'
						}
					}
				},
				grid: {
					show: true,
					borderColor: themeColors.gridBorderColor,
					strokeDashArray: 4,
					yaxis: { lines: { show: true } },
					xaxis: { lines: { show: false } }
				},
				tooltip: {
					y: { formatter: (val: number) => `${val.toFixed(1)} points` },
					theme: themeColors.tooltipTheme
				},
				states: {
					hover: { filter: { type: 'darken', value: 0.9 } }
				}
			};
		} else {
			columnChartOptions = null;
		}
	} else {
		pieChartOptions = null;
		columnChartOptions = null;
	}
</script>

<Header>
	<!-- Main page container with background and text colors -->
	<div
		class="min-h-screen bg-slate-50 text-slate-800 selection:bg-blue-500 selection:text-white dark:bg-slate-900 dark:text-slate-200"
	>
		<div class="container mx-auto px-4 py-8 sm:px-6 md:py-12 lg:px-8">
			{#if data.error}
				<!-- Error State -->
				<div
					class="flex flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50 p-6 md:p-10 dark:border-red-700 dark:bg-red-900/30"
				>
					<Alert color="danger" class="w-full max-w-xl !border-none !bg-transparent !p-0">
						<!-- Flowbite Alert custom styling -->
						<h3 class="mb-2 text-xl font-semibold text-red-700 dark:text-red-300">
							<span class="font-bold">Error!</span> Dashboard Unavailable
						</h3>
						<p class="text-red-600 dark:text-red-400">{data.error}</p>
					</Alert>
				</div>
			{:else if data.dashboardData?.data}
				<!-- Main Dashboard Content -->
				<h1
					class="mb-8 text-center text-3xl font-bold text-slate-900 sm:text-left sm:text-4xl md:mb-10 dark:text-white"
				>
					{data.dashboardData.message}
				</h1>

				<!-- Key Metrics Section -->
				<section aria-labelledby="key-metrics-title" class="mb-10 md:mb-12">
					<h2 id="key-metrics-title" class="sr-only">Key Metrics</h2>
					<div class="grid grid-cols-1 gap-5 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
						{#each [{ title: 'Total Students', value: data.dashboardData.data.total_students, unit: '' }, { title: 'Active Programs', value: data.dashboardData.data.total_programs, unit: '' }, { title: 'Overall Avg. Score', value: data.dashboardData.data.overall_average_score, unit: '', format: (v) => v?.toFixed(1) || 'N/A' }, { title: 'Learn Guide Completion', value: data.dashboardData.data.learn_guide_completion_rate, unit: '%', format: (v) => (v != null ? v.toFixed(0) + '%' : 'N/A') }] as metric}
							<div
								class="transform rounded-xl bg-white p-5 shadow-lg transition-all duration-300 ease-in-out hover:-translate-y-1 hover:shadow-2xl md:p-6 dark:bg-slate-800"
							>
								<h3 class="truncate text-sm font-medium text-slate-500 dark:text-slate-400">
									{metric.title}
								</h3>
								<p
									class="mt-1 text-3xl font-semibold tracking-tight text-slate-900 dark:text-white"
								>
									{metric.format ? metric.format(metric.value) : metric.value}
								</p>
							</div>
						{/each}
					</div>
				</section>

				<!-- Charts Section -->
				<section aria-labelledby="charts-title" class="mb-10 md:mb-12">
					<h2 id="charts-title" class="sr-only">Program Statistics</h2>
					<div class="grid grid-cols-1 gap-5 md:gap-6 lg:grid-cols-2">
						<div class="rounded-xl bg-white p-5 shadow-lg md:p-6 dark:bg-slate-800">
							<h3 class="mb-1 text-xl font-semibold text-slate-900 dark:text-white">
								Students by Program
							</h3>
							<p class="mb-4 text-sm text-slate-500 dark:text-slate-400">
								Distribution across academic programs.
							</p>
							<div class="flex min-h-[340px] items-center justify-center">
								{#if pieChartOptions}
									<Chart options={pieChartOptions} class="w-full" />
								{:else}
									<p class="text-center text-slate-500 dark:text-slate-400">
										No program data for chart.
									</p>
								{/if}
							</div>
						</div>

						<div class="rounded-xl bg-white p-5 shadow-lg md:p-6 dark:bg-slate-800">
							<h3 class="mb-1 text-xl font-semibold text-slate-900 dark:text-white">
								Average Score by Program
							</h3>
							<p class="mb-4 text-sm text-slate-500 dark:text-slate-400">
								Comparing average performance per program.
							</p>
							<div class="flex min-h-[340px] items-center justify-center">
								{#if columnChartOptions}
									<Chart options={columnChartOptions} class="w-full" />
								{:else}
									<p class="text-center text-slate-500 dark:text-slate-400">
										No average score data for chart.
									</p>
								{/if}
							</div>
						</div>
					</div>
				</section>

				<!-- Actionable Lists (kept commented, but structure is there) -->
				<section aria-labelledby="actionable-lists-title" class="mb-10 md:mb-12">
					<h2
						id="actionable-lists-title"
						class="mb-6 text-center text-2xl font-semibold text-slate-900 sm:text-left dark:text-white"
					>
						Student Insights
					</h2>
					<div class="grid grid-cols-1 gap-5 md:grid-cols-2 md:gap-6">
						{#if data.dashboardData.data.low_performing_students?.length}
							<div class="rounded-xl bg-white p-5 shadow-lg md:p-6 dark:bg-slate-800">
								<h3 class="mb-3 text-xl font-semibold text-slate-900 dark:text-white">
									Students Requiring Attention
									<span class="text-sm font-normal text-slate-500 dark:text-slate-400"
										>({data.dashboardData.data.students_at_risk_count})</span
									>
								</h3>
								<ul class="space-y-3">
									{#each data.dashboardData.data.low_performing_students.slice(0, 5) as student}
										<li class="text-sm">
											<a
												href="/students/{student.student_id}/edit"
												class="text-slate-600 transition-colors hover:text-blue-600 hover:underline dark:text-slate-300 dark:hover:text-blue-400"
											>
												{student.first_name}
												{student.last_name} - Score: {student.avg_test_score?.toFixed(1) || 'N/A'}
											</a>
										</li>
									{/each}
								</ul>
							</div>
						{/if}
						{#if data.dashboardData.data.recent_students?.length}
							<div class="rounded-xl bg-white p-5 shadow-lg md:p-6 dark:bg-slate-800">
								<h3 class="mb-3 text-xl font-semibold text-slate-900 dark:text-white">
									Recently Added Students
								</h3>
								<ul class="space-y-3">
									{#each data.dashboardData.data.recent_students.slice(0, 5) as student}
										<li class="text-sm text-slate-600 dark:text-slate-300">
											{student.first_name}
											{student.last_name} ({student.program || 'N/A'})
										</li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>
				</section>

				<!-- Call to Action / Navigation -->
				<section class="mt-12 text-center md:mt-16">
					<a
						href="/manage"
						class="inline-block transform rounded-lg bg-blue-600 px-8 py-3 text-base font-medium text-white no-underline shadow-md transition-all duration-150 ease-in-out hover:scale-105 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-50 focus:outline-none dark:focus:ring-offset-slate-900"
					>
						Manage Students
					</a>
				</section>
			{:else if data.dashboardData && !data.dashboardData.data}
				<!-- State: Welcome message but no specific stats data -->
				<div class="py-10 text-center">
					<h1 class="mb-8 text-3xl font-bold text-slate-900 sm:text-4xl dark:text-white">
						{data.dashboardData.message}
					</h1>
					<Alert color="warning" class="mx-auto max-w-lg">
						<!-- Centered Alert -->
						<span class="font-medium">Notice:</span> No dashboard statistics are available at the moment.
					</Alert>
				</div>
			{:else}
				<!-- Loading State -->
				<div class="flex min-h-[calc(100vh-200px)] flex-col items-center justify-center">
					<div aria-label="Loading..." role="status" class="flex items-center space-x-2">
						<svg class="h-10 w-10 animate-spin stroke-blue-600" viewBox="0 0 256 256">
							<line
								x1="128"
								y1="32"
								x2="128"
								y2="64"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
							<line
								x1="195.9"
								y1="60.1"
								x2="173.3"
								y2="82.7"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
							<line
								x1="224"
								y1="128"
								x2="192"
								y2="128"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
							<line
								x1="195.9"
								y1="195.9"
								x2="173.3"
								y2="173.3"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
							<line
								x1="128"
								y1="224"
								x2="128"
								y2="192"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
							<line
								x1="60.1"
								y1="195.9"
								x2="82.7"
								y2="173.3"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
							<line
								x1="32"
								y1="128"
								x2="64"
								y2="128"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
							<line
								x1="60.1"
								y1="60.1"
								x2="82.7"
								y2="82.7"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="24"
							></line>
						</svg>
						<span class="text-lg font-medium text-slate-600 dark:text-slate-300"
							>Loading dashboard...</span
						>
					</div>
				</div>
			{/if}
		</div>
	</div>
</Header>
