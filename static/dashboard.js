document.addEventListener("DOMContentLoaded", () => {



    // ==========================================
    // Pass 5: Historical Stock Movement Trends
    // ==========================================

    const trendsCanvas = document.getElementById(
        "stockTrendsChart"
    );

    const trendsDataElement = document.getElementById(
        "stockTrendsData"
    );

    if (trendsCanvas && trendsDataElement) {
        const trends = JSON.parse(
            trendsDataElement.textContent
        );

        new Chart(trendsCanvas, {
            type: "line",

            data: {
                labels: trends.labels,
                datasets: [
                    {
                        label: "Stock In",
                        data: trends.stock_in,
                        borderColor: "#16a34a",
                        backgroundColor: "#16a34a",
                        tension: 0.3,
                    },
                    {
                        label: "Stock Out",
                        data: trends.stock_out,
                        borderColor: "#dc2626",
                        backgroundColor: "#dc2626",
                        tension: 0.3,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    mode: "index",
                    intersect: false,
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Units",
                        },
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 8,
                        },
                    },
                },
            },
        });
    }


    // ==========================================
    // Category Inventory Valuation Chart
    // ==========================================

    const categoryChartCanvas = document.getElementById(
        "categoryValuationChart"
    );

    const categoryDataElement = document.getElementById(
        "categoryValuationData"
    );

    if (categoryChartCanvas && categoryDataElement) {
        const categoryValuations = JSON.parse(
            categoryDataElement.textContent
        );

        const categories = Object.keys(categoryValuations);
        const inventoryValues = Object.values(categoryValuations);

        new Chart(categoryChartCanvas, {
            type: "bar",

            data: {
                labels: categories,
                datasets: [
                    {
                        label: "Inventory Value (₦)",
                        data: inventoryValues,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.raw;

                                return `₦${value.toLocaleString()}`;
                            },
                        },
                    },
                },
            },
        });
    }


    // ==========================================
    // Supplier Inventory Valuation Chart
    // ==========================================

    const supplierChartCanvas = document.getElementById(
        "supplierValuationChart"
    );

    const supplierDataElement = document.getElementById(
        "supplierValuationData"
    );

    if (supplierChartCanvas && supplierDataElement) {
        const supplierValuations = JSON.parse(
            supplierDataElement.textContent
        );

        const suppliers = Object.keys(supplierValuations);
        const inventoryValues = Object.values(supplierValuations);

        new Chart(supplierChartCanvas, {
            type: "bar",

            data: {
                labels: suppliers,
                datasets: [
                    {
                        label: "Inventory Value (₦)",
                        data: inventoryValues,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.raw;

                                return `₦${value.toLocaleString()}`;
                            },
                        },
                    },
                },
            },
        });
    }


    // ==========================================
    // Low-Stock Overview Chart
    // ==========================================

    const lowStockChartCanvas = document.getElementById(
        "lowStockChart"
    );

    const lowStockDataElement = document.getElementById(
        "lowStockData"
    );

    if (lowStockChartCanvas && lowStockDataElement) {
        const lowStockProducts = JSON.parse(
            lowStockDataElement.textContent
        );

        const productNames = lowStockProducts.map(
            (product) => product.name
        );

        const currentQuantities = lowStockProducts.map(
            (product) => product.quantity
        );

        const lowStockLevels = lowStockProducts.map(
            (product) => product.low_stock_level
        );

        new Chart(lowStockChartCanvas, {
            type: "bar",

            data: {
                labels: productNames,
                datasets: [
                    {
                        label: "Current Quantity",
                        data: currentQuantities,
                    },
                    {
                        label: "Low Stock Level",
                        data: lowStockLevels,
                    },
                ],
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }


    // ==========================================
    // AI Inventory Insights
    // ==========================================

    const aiButton = document.getElementById(
        "generateAiInsights"
    );

    const aiResult = document.getElementById(
        "aiInsightsResult"
    );

    const aiStatus = document.getElementById(
        "aiInsightsStatus"
    );

    const csrfInput = document.getElementById(
        "aiCsrfToken"
    );


    // Safely format AI-generated text without using innerHTML.
    const displayAiAnalysis = (analysis) => {
        aiResult.replaceChildren();

        const lines = analysis
            .split("\n")
            .map((line) => line.trim())
            .filter((line) => line);

        if (lines.length === 0) {
            const paragraph = document.createElement("p");

            paragraph.textContent =
                "AI analysis did not return any content.";

            aiResult.appendChild(paragraph);

            return;
        }

        let list = null;

        lines.forEach((line) => {
            // Format Markdown-style headings safely.
            if (line.startsWith("## ")) {
                list = null;

                const heading = document.createElement("h3");

                heading.textContent = line
                    .slice(3)
                    .replace(/\*\*/g, "");

                aiResult.appendChild(heading);

                return;
            }

            // Format bullet points safely.
            if (line.startsWith("- ")) {
                if (!list) {
                    list = document.createElement("ul");
                    list.classList.add("ai-result-list");
                    aiResult.appendChild(list);
                }

                const item = document.createElement("li");

                item.textContent = line
                    .slice(2)
                    .replace(/\*\*/g, "");

                list.appendChild(item);

                return;
            }

            list = null;

            const paragraph = document.createElement("p");

            paragraph.textContent = line.replace(
                /\*\*/g,
                ""
            );

            aiResult.appendChild(paragraph);
        });
    };


    if (
        aiButton
        && aiResult
        && aiStatus
        && csrfInput
    ) {
        aiButton.addEventListener(
            "click",
            async () => {
                aiButton.disabled = true;

                aiStatus.textContent =
                    "Generating AI inventory analysis...";

                aiResult.textContent = "";

                const formData = new FormData();

                formData.append(
                    "csrf_token",
                    csrfInput.value
                );

                try {
                    const response = await fetch(
                        "/ai-insights",
                        {
                            method: "POST",
                            body: formData,
                            credentials: "same-origin",
                        }
                    );

                    let data;

                    try {
                        data = await response.json();
                    } catch {
                        throw new Error(
                            "The server returned an invalid response."
                        );
                    }

                    if (!response.ok) {
                        throw new Error(
                            data.detail
                            || "Unable to generate AI analysis."
                        );
                    }

                    aiStatus.textContent =
                        "AI analysis generated successfully.";

                    displayAiAnalysis(
                        data.ai_analysis
                    );
                } catch (error) {
                    aiStatus.textContent =
                        "AI analysis could not be generated.";

                    aiResult.textContent =
                        error.message;
                } finally {
                    aiButton.disabled = false;
                }
            }
        );
    }
});