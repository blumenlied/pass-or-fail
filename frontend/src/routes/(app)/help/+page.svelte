<!-- src/routes/(app)/help/+page.svelte -->
<script lang="ts">
  import Header from '../Header.svelte';
  import { Accordion, AccordionItem, A } from 'flowbite-svelte';
  import { ChevronDownOutline, ChevronRightOutline } from 'flowbite-svelte-icons';

  const generalFaqs = [
    {
      question: "Can you add students to the system?",
      answer: "Yes. You can add new students, update existing student information, and delete selected students from the system through the Management Page."
    },
    {
      question: "How do you predict whether a student will pass the certification exam or not?",
      answer: "We utilize an ensemble machine learning model. This model combines the strengths of both Random Forest and Decision Tree algorithms to predict the probability of a student successfully passing their certification exam based on their performance data."
    },
    {
      question: "Where can I see the student's predicted pass probability?",
      answer: "The Prediction Page allows you to generate these predictions. You can view the probability for individual students or for an entire class. The results are typically displayed with the probability score and a 'Pass'/'Fail' category."
    },
    {
        question: "What does the Dashboard show?",
        answer: "The Dashboard provides a high-level summary of overall student performance, focusing on students who are planning to take the certification exam. It includes key metrics like total students, average scores, and program distributions."
    }
  ];

  const devFaqs = [
    {
      question: "What are the main Python backend dependencies?",
      answer: `
        The core Python dependencies include:
        <ul class="list-disc list-inside space-y-1 mt-2 text-sm">
          <li><code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">fastapi</code>: For building the API.</li>
          <li><code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">sqlalchemy</code>: For database ORM.</li>
          <li><code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">uvicorn</code>: ASGI server to run FastAPI.</li>
          <li><code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">python-jose[cryptography]</code>: For JWT.</li>
          <li><code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">passlib[bcrypt]</code>: For password hashing.</li>
          <li><code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">python-multipart</code>: For form data.</li>
          <li><code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">joblib</code>, <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">pandas</code>, <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">numpy</code>, <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">scikit-learn</code>: For ML.</li>
        </ul>
        Install via: <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">pip install fastapi sqlalchemy "uvicorn[standard]" python-jose[cryptography] passlib[bcrypt] python-multipart joblib pandas numpy scikit-learn</code>
      `
    },
    {
      question: "What other dependencies are needed?",
      answer: `
        For the frontend:
        <ul class="list-disc list-inside space-y-1 mt-2 text-sm">
          <li><strong>Node.js & npm/yarn/pnpm</strong></li>
          <li>Dependencies in <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">frontend/package.json</code>. Install with <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">npm install</code>.</li>
        </ul>
      `
    },
    {
      question: "How do I start the program (backend and frontend)?",
      answer: `
        1.  <strong>Backend:</strong>
            <ul class="list-disc list-inside space-y-1 mt-1 text-sm">
                <li>Go to <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">.../backend</code>.</li>
                <li>Run: <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">uvicorn app.main:app --reload</code>.</li>
            </ul>
        2.  <strong>Frontend:</strong>
            <ul class="list-disc list-inside space-y-1 mt-2 text-sm">
                <li>Go to <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">.../frontend</code>.</li>
                <li>Run: <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">npm run dev</code>.</li>
            </ul>
      `
    },
    {
      question: "The 'npm run dev' command fails with 'running scripts is disabled' error on Windows. How to fix?",
      answer: `
        <ul class="list-disc list-inside space-y-1 mt-1 text-sm">
            <li>Open <strong>PowerShell as Administrator</strong>.</li>
            <li>Run: <code class="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">Set-ExecutionPolicy RemoteSigned</code>.</li>
            <li>Confirm with 'Y' or 'A'.</li>
        </ul>
      `
    },
    {
        question: "Where is the machine learning model stored and how is it loaded?",
        answer: "ML model components are in <code class=\"bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs\">app/ml/</code>. Loaded at FastAPI startup via <code class=\"bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded text-xs\">app/main.py</code>."
    }
  ];


  let openUserGuide = true;
  let openGeneralFaqs = false;
  let openDevFaqs = false;

  // Props for Accordion customization - less aggressive overrides
  const accordionHeaderProps = {
    class: "!py-4 !px-0 text-slate-800 dark:!text-slate-100 hover:!bg-slate-50 dark:hover:!bg-slate-700/50 transition-colors"
  };
  const accordionContentProps = {
    class: "!p-0 pt-2 pb-4 text-slate-600 dark:text-slate-300"
  };
</script>

<Header>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 selection:bg-blue-500 selection:text-white">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      <h1 class="text-3xl sm:text-4xl font-bold mb-10 text-slate-900 dark:text-white text-center">
        Help & Support Center
      </h1>

      <!-- User Guide Section -->
      <section aria-labelledby="user-guide-title" class="mb-10">
        <div class="bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-xl shadow-lg">
          <button
            on:click={() => openUserGuide = !openUserGuide}
            aria-expanded={openUserGuide}
            aria-controls="user-guide-content"
            class="flex justify-between items-center w-full text-left text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white mb-4 hover:text-blue-600 dark:hover:text-blue-400 transition-colors focus:outline-none"
          >
            User Guide
            <ChevronDownOutline class="w-5 h-5 sm:w-6 sm:h-6 transition-transform duration-200 {openUserGuide ? 'rotate-180' : ''}" />
          </button>
          {#if openUserGuide}
          <div id="user-guide-content" class="space-y-6 text-slate-600 dark:text-slate-300 prose prose-slate dark:prose-invert max-w-none prose-headings:font-semibold prose-headings:text-slate-700 prose-headings:dark:text-slate-200 prose-code:bg-slate-200 prose-code:dark:bg-slate-700 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs">
            <p>Welcome to the Intelligent Student Performance Prediction system. This guide will walk you through the main features of the application.</p>
            <div>
              <h3>1. Login Page</h3>
              <p>This is the entry point to the application. You will need to log in using your assigned faculty credentials to access the system's features.</p>
            </div>
            <div>
              <h3>2. Dashboard</h3>
              <p>Upon successful login, you'll be directed to the Dashboard. This page provides a comprehensive summary of overall student performance, with a particular focus on students currently preparing for the certification exam. Key metrics and visualizations help you quickly grasp important trends.</p>
            </div>
            <div>
              <h3>3. Management Page</h3>
              <p>The Management Page is your hub for student administration. Here, you can view a detailed list of all students, add new students to the system, update their information (such as test scores, program details), and remove students if necessary.</p>
            </div>
            <div>
              <h3>4. Prediction Page</h3>
              <p>This powerful feature allows you to leverage the machine learning model to generate predictions. You can predict the probability of an individual student passing their certification exam or run predictions for an entire class (program and section). The results are based on the students' current performance data.</p>
            </div>
            <div>
              <h3>5. Help Page</h3>
              <p>You are here! This page provides essential information, including this User Guide, answers to frequently asked questions (FAQs) for general users, and technical FAQs for developers or those interested in the system's setup.</p>
            </div>
          </div>
          {/if}
        </div>
      </section>

      <!-- General FAQs Section -->
      <section aria-labelledby="general-faqs-title" class="mb-10">
         <div class="bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-xl shadow-lg">
            <button
                on:click={() => openGeneralFaqs = !openGeneralFaqs}
                aria-expanded={openGeneralFaqs}
                aria-controls="general-faqs-content"
                class="flex justify-between items-center w-full text-left text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white mb-4 hover:text-blue-600 dark:hover:text-blue-400 transition-colors focus:outline-none"
            >
                General FAQs
                <ChevronDownOutline class="w-5 h-5 sm:w-6 sm:h-6 transition-transform duration-200 {openGeneralFaqs ? 'rotate-180' : ''}" />
            </button>
            {#if openGeneralFaqs}
            <div id="general-faqs-content">
                <Accordion flush> <!-- Try with 'flush' for no outer borders -->
                    {#each generalFaqs as faq, i (i)}
                        <AccordionItem
                          headerClass={accordionHeaderProps.class}
                          contentClass={accordionContentProps.class}
                        >
                        {#snippet header()}
                            <span slot="header" class="text-base font-medium w-full">{faq.question}</span>
{/snippet}
                            <!-- Content for AccordionItem -->
                            <div class="text-sm leading-relaxed space-y-2 prose prose-sm prose-slate dark:prose-invert max-w-none prose-code:bg-slate-200 prose-code:dark:bg-slate-700 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs">
                                {@html faq.answer}
                            </div>
                        </AccordionItem>
                    {/each}
                </Accordion>
            </div>
            {/if}
        </div>
      </section>

      <!-- Developer FAQs Section -->
      <section aria-labelledby="dev-faqs-title" class="mb-10">
        <div class="bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-xl shadow-lg">
            <button
                on:click={() => openDevFaqs = !openDevFaqs}
                aria-expanded={openDevFaqs}
                aria-controls="dev-faqs-content"
                class="flex justify-between items-center w-full text-left text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white mb-4 hover:text-blue-600 dark:hover:text-blue-400 transition-colors focus:outline-none"
            >
                Developer FAQs & Setup
                <ChevronDownOutline class="w-5 h-5 sm:w-6 sm:h-6 transition-transform duration-200 {openDevFaqs ? 'rotate-180' : ''}" />
            </button>
            {#if openDevFaqs}
            <div id="dev-faqs-content">
                <Accordion flush> <!-- Try with 'flush' for no outer borders -->
                    {#each devFaqs as faq, i (i)}
                         <AccordionItem
                            headerClass={accordionHeaderProps.class}
                            contentClass={accordionContentProps.class}
                         >
                         {#snippet header()}
                            <span slot="header" class="text-base font-medium w-full">{faq.question}</span>
{/snippet}
                            <!-- Content for AccordionItem -->
                            <div class="text-sm leading-relaxed space-y-2 prose prose-sm prose-slate dark:prose-invert max-w-none prose-code:bg-slate-200 prose-code:dark:bg-slate-700 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs">
                                {@html faq.answer}
                            </div>
                        </AccordionItem>
                    {/each}
                </Accordion>
            </div>
            {/if}
        </div>
      </section>

      <footer class="mt-12 text-center text-sm text-slate-500 dark:text-slate-400">
        <p>If you encounter any issues not covered here, please contact the system administrator or development team.</p>
      </footer>

    </div>
  </div>
</Header>
