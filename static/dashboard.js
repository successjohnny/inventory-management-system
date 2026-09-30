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

    // Low-Stock Overview Chart
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
});