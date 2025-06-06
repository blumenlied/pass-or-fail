<script>
	import Header from '../Header.svelte'; 
	import { onMount } from 'svelte';
	import { writable, get } from 'svelte/store';

	export let data; // From +page.server.js

	const API_BASE_URL = 'http://localhost:8000';

	let students = writable(data.students || []);
	let allPrograms = writable([]);
	// ... other store initializations ...
	let selectedStudentId = writable('');
	let selectedProgram = writable('');
	let selectedSection = writable('');
	let sectionsForSelectedProgram = writable([]);
	let studentPredictionResult = writable(null);
	let classPredictionResults = writable([]);
	let isLoadingStudentPrediction = writable(false);
	let isLoadingClassPrediction = writable(false);
	let studentSectionError = writable('');
	let classSectionError = writable('');

    let clientAuthToken = ''; // THIS IS THE CRITICAL VARIABLE

    $: {
        students.set(data.students || []);
        if (data.students && data.students.length > 0) {
            const uniquePrograms = [...new Set(data.students.map(s => s.program))].sort();
            allPrograms.set(uniquePrograms);
        } else {
            allPrograms.set([]);
        }
    }

    onMount(() => {
        clientAuthToken = localStorage.getItem('authToken'); // Get token from localStorage
        if (!clientAuthToken) {
            console.error("CLIENT FATAL onMount: authToken NOT FOUND in localStorage. Client-side predictions WILL FAIL.");
            // Potentially set an error message for the user here
            studentSectionError.set("Authentication error. Please log out and log in again.");
            classSectionError.set("Authentication error. Please log out and log in again.");
        } else {
            console.log("Client onMount: authToken retrieved from localStorage:", clientAuthToken.substring(0, 20) + "...");
        }
    });

	async function fetchApi(url, method = 'GET', body = null) {
		console.log(`Client Fetching API: ${method} ${url}`);
		console.log(`Token being used by fetchApi: '${clientAuthToken ? clientAuthToken.substring(0, 20) + "..." : "!!! TOKEN IS EMPTY OR UNDEFINED !!!"}'`);

		const headers = { 'Content-Type': 'application/json' };

		if (clientAuthToken && typeof clientAuthToken === 'string' && clientAuthToken.trim() !== '') {
			headers['Authorization'] = `Bearer ${clientAuthToken}`; // Notice the space after 'Bearer'
			console.log('Authorization header IS BEING SET with value:', headers['Authorization'].substring(0, 30) + "...");
		} else {
			console.error('CRITICAL in fetchApi: clientAuthToken is missing or invalid. Authorization header NOT SET. This will cause 401.');
            if (method === 'POST' || method === 'PUT' || method === 'DELETE' || url.includes("predict") || url.includes("dashboard")) { // Add other protected patterns
                 throw new Error("Client authentication token is missing. Action aborted.");
            }
		}

		const options = { method, headers };
		if (body && (method === 'POST' || method === 'PUT')) {
			options.body = JSON.stringify(body);
		}

		try {
			const response = await fetch(url, options); // This is the browser's fetch
			if (!response.ok) { // Line 74 error happens here
				let errorDetail = `HTTP error ${response.status}: ${response.statusText}`;
				try {
					const errorData = await response.json();
					errorDetail = errorData.detail || errorDetail;
				} catch (jsonError)
				console.error(`Client API Error for ${url}: ${errorDetail}`); // Line 81 log
				throw new Error(errorDetail);
			}
            if (response.status === 204 || response.headers.get("content-length") === "0") {
                return (method === 'GET' || method === 'POST') ? [] : null;
            }
			return await response.json();
		} catch (err) {
			console.error(`Client Fetch API function error for ${url}:`, err); // Line 89 log
			throw err;
		}
	}

    $: currentSelectedProgram = $selectedProgram;
    $: {
        if (currentSelectedProgram) {
            const currentStudentsList = get(students);
            const sections = [...new Set(currentStudentsList.filter(s => s.program === currentSelectedProgram).map(s => s.section))].sort();
            sectionsForSelectedProgram.set(sections);
			selectedSection.set('');
        } else {
            sectionsForSelectedProgram.set([]);
            selectedSection.set('');
        }
    }

	async function handlePredictForStudent() {
        const studentIdVal = get(selectedStudentId);
		if (!studentIdVal) {
			studentSectionError.set('Please select a student.');
			return;
		}
		isLoadingStudentPrediction.set(true);
		studentPredictionResult.set(null);
		studentSectionError.set('');
		try { // Line 119 is inside here
			const result = await fetchApi(`${API_BASE_URL}/students/${studentIdVal}/predict`, 'POST');
			studentPredictionResult.set(result);
            if (!result) studentSectionError.set('Prediction returned no data.');
		} catch (e) {
			studentSectionError.set(`Error predicting for student: ${e.message}`);
		} finally {
			isLoadingStudentPrediction.set(false);
		}
	}

	async function handleTriggerClassPredictions() {
        const programVal = get(selectedProgram);
        const sectionVal = get(selectedSection);
		if (!programVal || !sectionVal) {
			classSectionError.set('Please select both a program and a section.');
			return;
		}
		isLoadingClassPrediction.set(true);
		classPredictionResults.set([]);
		classSectionError.set('');
		try {
			const results = await fetchApi(`${API_BASE_URL}/predictions/class/${programVal}/${sectionVal}`, 'POST');
			classPredictionResults.set(results || []);
            if (!results || results.length === 0) {
                classSectionError.set('No predictions generated (perhaps no eligible students).');
            }
		} catch (e) {
			classSectionError.set(`Error predicting for class: ${e.message}`);
		} finally {
			isLoadingClassPrediction.set(false);
		}
	}
</script>

<!-- Your HTML template -->
<Header>
	<main class="container mx-auto p-4">
		<h1 class="mb-6 text-2xl font-bold text-gray-800">Generate Exam Predictions</h1>

		{#if $students.length === 0 && data.students && data.students.length === 0}
			<!-- Check initial server data too -->
			<div class="mb-4 rounded-lg bg-yellow-100 p-4 text-sm text-yellow-800" role="alert">
				<span class="font-medium">No student data available.</span> Please add students through the student
				management page before attempting predictions.
			</div>
		{:else}
			<!-- Predict for a Single Student -->
			<section class="mb-8 rounded-lg border border-gray-200 bg-white p-6 shadow-xl">
				<h2 class="mb-4 text-xl font-semibold text-gray-700">Single Student Prediction</h2>
				<div class="mb-4">
					<label for="student-select" class="mb-1 block text-sm font-medium text-gray-700"
						>Select Student:</label
					>
					<select
						id="student-select"
						bind:value={$selectedStudentId}
						class="mt-1 block w-full rounded-md border-gray-300 py-2 pr-10 pl-3 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none sm:text-sm"
						disabled={$students.length === 0}
					>
						<option value="" disabled>-- Select a Student --</option>
						{#each $students as student (student.student_id)}
							<option value={student.student_id}
								>{student.first_name} {student.last_name} (ID: {student.student_id})</option
							>
						{/each}
					</select>
				</div>
				<button
					on:click={handlePredictForStudent}
					disabled={$isLoadingStudentPrediction || !$selectedStudentId}
					class="rounded bg-indigo-600 px-4 py-2 font-bold text-white transition duration-150 ease-in-out hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
				>
					{#if $isLoadingStudentPrediction}
						Processing...
					{:else}
						Predict for Selected Student
					{/if}
				</button>

				{#if $studentSectionError}
					<p class="mt-2 text-sm text-red-600">Error: {$studentSectionError}</p>
				{/if}

				{#if $studentPredictionResult}
					<div class="mt-4 rounded border border-indigo-200 bg-indigo-50 p-4">
						<h3 class="font-semibold text-indigo-800">Prediction Result:</h3>
						<p><strong>Student ID:</strong> {$studentPredictionResult.student_id}</p>
						<p><strong>Date:</strong> {$studentPredictionResult.date}</p>
						<p>
							<strong>Probability (Pass):</strong>
							{($studentPredictionResult.predicted_score * 100).toFixed(2)}%
						</p>
						<p>
							<strong>Outcome:</strong>
							<span
								class:text-green-700={$studentPredictionResult.category === 'Pass'}
								class:text-red-700={$studentPredictionResult.category === 'Fail'}
								>{$studentPredictionResult.category}</span
							>
						</p>
						<p><strong>Model:</strong> {$studentPredictionResult.model_type}</p>
					</div>
				{/if}
			</section>

			<!-- Predict for a Class -->
			<section class="mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow-xl">
				<h2 class="mb-4 text-xl font-semibold text-gray-700">Class Predictions</h2>
				{#if $allPrograms.length === 0}
					<p class="text-sm text-gray-500">
						No programs available for selection (likely no students with programs exist).
					</p>
				{:else}
					<div class="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
						<div>
							<label for="program-select" class="mb-1 block text-sm font-medium text-gray-700"
								>Select Program:</label
							>
							<select
								id="program-select"
								bind:value={$selectedProgram}
								class="mt-1 block w-full rounded-md border-gray-300 py-2 pr-10 pl-3 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none sm:text-sm"
							>
								<option value="" disabled>-- Select Program --</option>
								{#each $allPrograms as program (program)}
									<option value={program}>{program}</option>
								{/each}
							</select>
						</div>
						<div>
							<label for="section-select" class="mb-1 block text-sm font-medium text-gray-700"
								>Select Section:</label
							>
							<select
								id="section-select"
								bind:value={$selectedSection}
								class="mt-1 block w-full rounded-md border-gray-300 py-2 pr-10 pl-3 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none sm:text-sm"
								disabled={!$selectedProgram || $sectionsForSelectedProgram.length === 0}
							>
								{#if !$selectedProgram}
									<option value="" disabled>-- Select program first --</option>
								{:else if $sectionsForSelectedProgram.length === 0}
									<option value="" disabled>-- No sections for program --</option>
								{:else}
									<option value="" disabled>-- Select Section --</option>
									{#each $sectionsForSelectedProgram as section (section)}
										<option value={section}>{section}</option>
									{/each}
								{/if}
							</select>
						</div>
					</div>
					<button
						on:click={handleTriggerClassPredictions}
						disabled={$isLoadingClassPrediction || !$selectedProgram || !$selectedSection}
						class="rounded bg-teal-600 px-4 py-2 font-bold text-white transition duration-150 ease-in-out hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
					>
						{#if $isLoadingClassPrediction}
							Processing...
						{:else}
							Predict for Entire Class
						{/if}
					</button>
				{/if}

				{#if $classSectionError}
					<p class="mt-2 text-sm text-red-600">Error: {$classSectionError}</p>
				{/if}

				{#if $classPredictionResults && $classPredictionResults.length > 0}
					<div class="mt-6">
						<h3 class="mb-2 text-lg font-medium text-gray-700">Generated Class Predictions:</h3>
						<p class="mb-2 text-sm text-gray-600">
							{$classPredictionResults.length} prediction(s) generated for {$selectedProgram} - {$selectedSection}.
						</p>
						<div class="max-h-96 overflow-x-auto rounded border">
							<table class="min-w-full divide-y divide-gray-200 text-sm">
								<thead class="sticky top-0 z-10 bg-gray-100"
									><tr class="text-left">
										<th class="px-4 py-2 font-semibold whitespace-nowrap text-gray-600"
											>Student ID</th
										>
										<th class="px-4 py-2 font-semibold whitespace-nowrap text-gray-600">Date</th>
										<th class="px-4 py-2 font-semibold whitespace-nowrap text-gray-600"
											>Prob (Pass)</th
										>
										<th class="px-4 py-2 font-semibold whitespace-nowrap text-gray-600">Outcome</th>
										<th class="px-4 py-2 font-semibold whitespace-nowrap text-gray-600">Model</th>
									</tr></thead
								>
								<tbody class="divide-y divide-gray-200 bg-white">
									{#each $classPredictionResults as pred (pred.prediction_id)}
										<tr class="text-left">
											<td class="px-4 py-2 whitespace-nowrap">{pred.student_id}</td>
											<td class="px-4 py-2 whitespace-nowrap">{pred.date}</td>
											<td class="px-4 py-2 whitespace-nowrap"
												>{(pred.predicted_score * 100).toFixed(1)}%</td
											>
											<td class="px-4 py-2 whitespace-nowrap"
												><span
													class:text-green-600={pred.category === 'Pass'}
													class:text-red-600={pred.category === 'Fail'}>{pred.category}</span
												></td
											>
											<td class="px-4 py-2 whitespace-nowrap">{pred.model_type}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				{/if}
			</section>
		{/if}
	</main>
</Header>

<style>
	.container {
		max-width: 1280px;
	}
	.max-h-96 {
		max-height: 24rem;
	}
	.sticky {
		position: sticky;
	}
	.top-0 {
		top: 0;
	}
	.z-10 {
		z-index: 10;
	}
</style>
