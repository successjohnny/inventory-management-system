document.addEventListener("DOMContentLoaded", () => {
    // Category Inventory Valuation Chart
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

    // Supplier Inventory Valuation Chart
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
});
