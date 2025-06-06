<script lang="ts">
	import {
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		Modal,
		TableSearch,
		Select
	} from 'flowbite-svelte'; // Added Select
	import AddStudentModal from '$lib/components/AddStudentModal.svelte';
	import EditStudentModal from '$lib/components/EditStudentModal.svelte';
	import { onMount } from 'svelte';
	import Header from '../Header.svelte'; // Assuming Header.svelte exists

	let showAddModal = false;
	let showEditModal = false;
	let studentToEdit: any = null;

	let showDeleteConfirmModal = false;
	let studentToDeleteId: number | null = null;
	let studentToDeleteName: string = '';

	let selectedStudentIds: Set<number> = new Set();
	let showBulkDeleteConfirmModal = false;

	let students: any[] = [];
	let searchTerm: string = ''; // For the search bar

	let selectedProgram: string = ''; // For Program filter, '' means All
	let selectedSection: string = ''; // For Section filter, '' means All

	// Derive unique programs and sections for dropdowns
	$: uniquePrograms = Array.from(new Set(students.map((s) => s.program).filter((p) => p))).sort();
	$: uniqueSections = Array.from(new Set(students.map((s) => s.section).filter((s) => s))).sort();

	// Reactive variable for filtered students based on searchTerm AND filters
	$: filteredStudents = students.filter((student) => {
		// Program filter
		const programMatch = selectedProgram === '' || student.program === selectedProgram;
		// Section filter
		const sectionMatch = selectedSection === '' || student.section === selectedSection;

		// Search term filter
		let termMatch = true;
		if (searchTerm.trim()) {
			const term = searchTerm.toLowerCase();
			// Helper to check if a value contains the search term
			const check = (val: any) => val != null && String(val).toLowerCase().includes(term);

			termMatch =
				check(student.student_id) ||
				check(student.first_name) ||
				check(student.last_name) ||
				check(student.program) || // Keep program/section in search for broader text search
				check(student.section);
		}

		return programMatch && sectionMatch && termMatch;
	});

	// Logic for the header "select all" checkbox, based on filtered (visible) students
	$: allFilteredSelected =
		filteredStudents.length > 0 &&
		filteredStudents.every((s) => selectedStudentIds.has(s.student_id));
	$: someFilteredSelected =
		filteredStudents.length > 0 &&
		filteredStudents.some((s) => selectedStudentIds.has(s.student_id));
	$: indeterminateFiltered = someFilteredSelected && !allFilteredSelected;

	async function loadStudents() {
		try {
			const response = await fetch('http://localhost:8000/students');
			if (!response.ok) throw new Error(await response.text());
			students = await response.json();
			selectedStudentIds.clear(); // Clear selections on new data load
			selectedStudentIds = new Set([...selectedStudentIds]); // Trigger reactivity
		} catch (error) {
			console.error('Error fetching students:', error);
			alert('Could not load students. Check console.');
		}
	}

	onMount(() => {
		loadStudents();
	});

	function openEditStudentModal(student: any) {
		studentToEdit = { ...student };
		showEditModal = true;
	}

	async function handleEditStudent(event: CustomEvent) {
		const updatedStudentData = event.detail;
		const studentId = updatedStudentData.student_id;
		const formData = new FormData();

		for (const [key, value] of Object.entries(updatedStudentData)) {
			if (key !== 'student_id' && key !== 'dob_is_date_object') {
				if (value !== null && value !== undefined) {
					formData.append(key, String(value));
				}
			}
		}
		if (updatedStudentData.dob !== null && updatedStudentData.dob !== undefined) {
			formData.set('dob', String(updatedStudentData.dob));
		}

		try {
			const response = await fetch(`http://localhost:8000/students/${studentId}`, {
				method: 'PUT',
				body: formData
			});
			if (response.ok) {
				await response.json();
				closeEditModal();
				await loadStudents();
			} else {
				const errorText = await response.text();
				alert(`Failed to update student: ${errorText}`);
				console.error('Failed to update student:', errorText);
			}
		} catch (err) {
			console.error('An error occurred while updating the student:', err);
			alert('An error occurred while updating the student.');
		}
	}

	function closeEditModal() {
		showEditModal = false;
		studentToEdit = null;
	}

	async function handleAddStudent(event: CustomEvent) {
		const newStudentData = event.detail;
		const formData = new FormData();

		for (const [key, value] of Object.entries(newStudentData)) {
			if (value !== null && value !== undefined) {
				formData.append(key, String(value));
			}
		}

		try {
			const response = await fetch('http://localhost:8000/students', {
				method: 'POST',
				body: formData
			});
			if (response.ok) {
				await response.json();
				showAddModal = false;
				await loadStudents();
			} else {
				const errorText = await response.text();
				alert(`Failed to add student: ${errorText}`);
				console.error('Failed to add student:', errorText);
			}
		} catch (err) {
			console.error('An error occurred while adding the student:', err);
			alert('An error occurred while adding the student.');
		}
	}

	function openDeleteConfirm(student: any) {
		studentToDeleteId = student.student_id;
		studentToDeleteName = `${student.first_name} ${student.last_name}`;
		showDeleteConfirmModal = true;
	}

	async function confirmDelete() {
		if (studentToDeleteId === null) return;
		try {
			const response = await fetch(`http://localhost:8000/students/${studentToDeleteId}`, {
				method: 'DELETE'
			});
			if (response.ok) {
				await loadStudents();
			} else {
				const errorText = await response.text();
				alert(`Failed to delete student: ${errorText}`);
				console.error('Failed to delete student:', errorText);
			}
		} catch (err) {
			console.error('Error deleting student:', err);
			alert('Error deleting student.');
		} finally {
			resetSingleDeleteModalState();
		}
	}

	function toggleSelectAll(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.checked) {
			filteredStudents.forEach((s) => selectedStudentIds.add(s.student_id));
		} else {
			filteredStudents.forEach((s) => selectedStudentIds.delete(s.student_id));
		}
		selectedStudentIds = new Set([...selectedStudentIds]);
	}

	function toggleStudentSelection(studentId: number, event: Event) {
		const target = event.target as HTMLInputElement;
		target.checked ? selectedStudentIds.add(studentId) : selectedStudentIds.delete(studentId);
		selectedStudentIds = new Set([...selectedStudentIds]);
	}

	function openBulkDeleteConfirmModalHandler() {
		if (selectedStudentIds.size === 0) return;
		showBulkDeleteConfirmModal = true;
	}

	async function confirmBulkDelete() {
		const idsToDelete = Array.from(selectedStudentIds);
		try {
			const deletePromises = idsToDelete.map((id) =>
				fetch(`http://localhost:8000/students/${id}`, { method: 'DELETE' }).then((res) => {
					if (!res.ok) throw new Error(`Failed to delete student ${id}: ${res.statusText}`);
					return res;
				})
			);
			await Promise.all(deletePromises);
		} catch (error) {
			console.error('Error during bulk delete:', error);
			alert('Some students could not be deleted. Check console.');
		} finally {
			showBulkDeleteConfirmModal = false;
			await loadStudents();
		}
	}

	function handleBulkDeleteModalClose() {
		showBulkDeleteConfirmModal = false;
	}

	function resetSingleDeleteModalState() {
		studentToDeleteId = null;
		studentToDeleteName = '';
		showDeleteConfirmModal = false;
	}
</script>

<Header>
	<div class="mb-4 flex flex-wrap items-center space-x-2">
		<button
			on:click={() => (showAddModal = true)}
			class="mb-2 rounded-lg bg-blue-700 px-5 py-2.5 text-center text-sm font-medium text-white hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 focus:outline-none md:mb-0 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
		>
			Add Student
		</button>
		<button
			on:click={openBulkDeleteConfirmModalHandler}
			disabled={selectedStudentIds.size === 0}
			class="mb-2 rounded-lg bg-red-700 px-5 py-2.5 text-center text-sm font-medium text-white hover:bg-red-800 focus:ring-4 focus:ring-red-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 md:mb-0 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-800"
		>
			Delete Selected ({selectedStudentIds.size})
		</button>

		<!-- Program Filter Dropdown -->
		<div class="mb-2 min-w-[150px] md:mb-0">
			<Select placeholder="Filter by Program" bind:value={selectedProgram} class="w-full text-sm">
				<option value="">All Programs</option>
				{#each uniquePrograms as program}
					<option value={program}>{program}</option>
				{/each}
			</Select>
		</div>

		<!-- Section Filter Dropdown -->
		<div class="mb-2 min-w-[150px] md:mb-0">
			<Select placeholder="Filter by Section" bind:value={selectedSection} class="w-full text-sm">
				<option value="">All Sections</option>
				{#each uniqueSections as section}
					<option value={section}>{section}</option>
				{/each}
			</Select>
		</div>
	</div>

	<AddStudentModal
		bind:open={showAddModal}
		on:submit={handleAddStudent}
		on:close={() => (showAddModal = false)}
	/>
	<EditStudentModal
		bind:open={showEditModal}
		student={studentToEdit}
		on:submit={handleEditStudent}
		on:close={closeEditModal}
	/>

	{#if showDeleteConfirmModal}
		<Modal
			class="motion-scale-in-[0.5] motion-opacity-in-[0%] motion-blur-in-[5px] motion-duration-[0.35s] motion-duration-[0.53s]/scale motion-delay-[0.16s]/blur"
			title="Confirm Deletion"
			bind:open={showDeleteConfirmModal}
			autoclose={false}
			size="xs"
			on:close={resetSingleDeleteModalState}
		>
			<div class="p-4 text-center">
				<svg
					aria-hidden="true"
					class="mx-auto mb-4 h-14 w-14 text-gray-400 dark:text-gray-200"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					></path></svg
				>
				<h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
					Are you sure you want to delete {studentToDeleteName} (ID: {studentToDeleteId})?
				</h3>
				<div class="flex justify-center space-x-4">
					<button
						on:click={resetSingleDeleteModalState}
						class="rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium text-gray-900 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white dark:focus:ring-gray-700"
					>
						Cancel
					</button>
					<button
						on:click={confirmDelete}
						class="rounded-lg bg-red-600 px-5 py-2.5 text-center text-sm font-medium text-white hover:bg-red-700 focus:ring-4 focus:ring-red-300 focus:outline-none dark:bg-red-500 dark:hover:bg-red-600 dark:focus:ring-red-900"
					>
						Yes, Delete
					</button>
				</div>
			</div>
		</Modal>
	{/if}

	<Modal
		class="motion-scale-in-[0.5] motion-opacity-in-[0%] motion-blur-in-[5px] motion-duration-[0.35s] motion-duration-[0.53s]/scale motion-delay-[0.16s]/blur"
		title="Confirm Bulk Deletion"
		bind:open={showBulkDeleteConfirmModal}
		autoclose={false}
		size="md"
		on:close={handleBulkDeleteModalClose}
	>
		<div class="p-4 text-center">
			<svg
				aria-hidden="true"
				class="mx-auto mb-4 h-14 w-14 text-gray-400 dark:text-gray-200"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
				><path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				></path></svg
			>
			<h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">
				Are you sure you want to delete {selectedStudentIds.size} student(s)?
			</h3>
			<div class="flex justify-center space-x-4">
				<button
					on:click={() => (showBulkDeleteConfirmModal = false)}
					class="rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium text-gray-900 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white dark:focus:ring-gray-700"
				>
					Cancel
				</button>
				<button
					on:click={confirmBulkDelete}
					class="rounded-lg bg-red-600 px-5 py-2.5 text-center text-sm font-medium text-white hover:bg-red-700 focus:ring-4 focus:ring-red-300 focus:outline-none dark:bg-red-500 dark:hover:bg-red-600 dark:focus:ring-red-900"
				>
					Yes, delete them
				</button>
			</div>
		</div>
	</Modal>

	<TableSearch
		placeholder="Search by ID or name..."
		bind:inputValue={searchTerm}
		hoverable={true}
		shadow={true}
		class="rounded-lg"
		tableClass="min-w-full text-sm text-left text-gray-500 dark:text-gray-400"
	>
		<TableHead
			class="bg-gray-50 text-xs text-gray-700 uppercase dark:bg-gray-700 dark:text-gray-400"
		>
			<TableHeadCell class="w-4 !p-4">
				<input
					type="checkbox"
					checked={allFilteredSelected}
					indeterminate={indeterminateFiltered}
					on:change={toggleSelectAll}
					disabled={filteredStudents.length === 0}
					class="h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
				/>
			</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">ID</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">First Name</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Last Name</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">DOB</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Program</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Section</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Test 1</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Test 2</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Test 3</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Avg Score</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3">Learn Guide</TableHeadCell>
			<TableHeadCell scope="col" class="px-6 py-3 text-center">Actions</TableHeadCell>
		</TableHead>
		<TableBody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
			{#if students.length === 0}
				<TableBodyRow class="bg-white dark:bg-gray-800">
					<TableBodyCell colspan="13" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400"
						>No students available.</TableBodyCell
					>
				</TableBodyRow>
			{:else if filteredStudents.length === 0}
				<TableBodyRow class="bg-white dark:bg-gray-800">
					<TableBodyCell colspan="13" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400"
						>No students match your search or filter criteria.</TableBodyCell
					>
				</TableBodyRow>
			{:else}
				{#each filteredStudents as student (student.student_id)}
					<TableBodyRow
						class={`border-b dark:border-gray-700 ${selectedStudentIds.has(student.student_id) ? 'bg-gray-100 dark:bg-gray-700' : 'bg-white hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-600'}`}
					>
						<TableBodyCell class="w-4 !p-4">
							<input
								type="checkbox"
								checked={selectedStudentIds.has(student.student_id)}
								on:change={(e) => toggleStudentSelection(student.student_id, e)}
								class="h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
							/>
						</TableBodyCell>
						<TableBodyCell
							class="px-6 py-4 font-medium whitespace-nowrap text-gray-900 dark:text-white"
							>{student.student_id}</TableBodyCell
						>
						<TableBodyCell class="px-6 py-4">{student.first_name}</TableBodyCell>
						<TableBodyCell class="px-6 py-4">{student.last_name}</TableBodyCell>
						<TableBodyCell class="px-6 py-4"
							>{student.dob
								? new Date(student.dob + 'T00:00:00').toLocaleDateString()
								: 'N/A'}</TableBodyCell
						>
						<TableBodyCell class="px-6 py-4">{student.program || 'N/A'}</TableBodyCell>
						<TableBodyCell class="px-6 py-4">{student.section || 'N/A'}</TableBodyCell>
						<TableBodyCell class="px-6 py-4">{student.test_1_score ?? 'N/A'}</TableBodyCell>
						<TableBodyCell class="px-6 py-4">{student.test_2_score ?? 'N/A'}</TableBodyCell>
						<TableBodyCell class="px-6 py-4">{student.test_3_score ?? 'N/A'}</TableBodyCell>
						<TableBodyCell class="px-6 py-4"
							>{student.avg_test_score != null
								? student.avg_test_score.toFixed(2)
								: 'N/A'}</TableBodyCell
						>
						<TableBodyCell class="px-6 py-4"
							>{student.learn_guide_completed ? 'Yes' : 'No'}</TableBodyCell
						>
						<TableBodyCell class="space-x-1 px-6 py-4 text-center whitespace-nowrap">
							<button
								on:click={() => openEditStudentModal(student)}
								class="rounded-lg bg-yellow-400 px-3 py-1.5 text-center text-xs font-medium text-gray-900 hover:bg-yellow-500 focus:ring-2 focus:ring-yellow-300 focus:outline-none dark:bg-yellow-400 dark:text-gray-900 dark:hover:bg-yellow-500 dark:focus:ring-yellow-300"
							>
								Edit
							</button>
						</TableBodyCell>
					</TableBodyRow>
				{/each}
			{/if}
		</TableBody>
	</TableSearch>
</Header>
