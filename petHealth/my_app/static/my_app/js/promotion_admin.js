document.addEventListener('DOMContentLoaded', function () {
    const categoryRow = document.querySelector('.field-categories');
    const productRow = document.querySelector('.field-products');

    if (!categoryRow || !productRow) {
        return; // Not on the right page or markup changed
    }

    // Add consistent styling to the form rows
    applyDjangoAdminStyling(categoryRow);
    applyDjangoAdminStyling(productRow);

    // Create wrapper for toggle switches - black monochrome theme
    const toggleWrapper = document.createElement('div');
    toggleWrapper.className = 'form-row field-promotion_type';
    toggleWrapper.style.cssText = `
        margin: 0;
        padding: 12px;
        background: #f8f8f8;
        border: 1px solid #e1e1e1;
        border-bottom: none;
    `;

    // Create title
    const toggleTitle = document.createElement('div');
    toggleTitle.innerHTML = '<label style="display: inline-block; margin-bottom: 8px; font-weight: bold; color: #333;">Loại khuyến mãi:</label>';
    toggleWrapper.appendChild(toggleTitle);

    // Create options container
    const optionsContainer = document.createElement('div');
    optionsContainer.style.cssText = `
        display: flex;
        gap: 15px;
        margin-top: 8px;
    `;

    // Create Category Option - Black theme
    const catOption = createToggleOption(
        'toggle-category',
        'Theo Danh mục'
    );

    // Create Product Option - Black theme (matching)
    const prodOption = createToggleOption(
        'toggle-product',
        'Theo Sản phẩm'
    );

    optionsContainer.appendChild(catOption.container);
    optionsContainer.appendChild(prodOption.container);
    toggleWrapper.appendChild(optionsContainer);

    // Insert wrapper before the category row
    categoryRow.parentNode.insertBefore(toggleWrapper, categoryRow);

    // Helper function to create styled toggle option - monochrome black theme
    function createToggleOption(id, labelText) {
        const container = document.createElement('div');
        container.style.cssText = `
            flex: 1;
        `;

        const label = document.createElement('label');
        label.htmlFor = id;
        label.style.cssText = `
            display: flex;
            align-items: center;
            padding: 10px 15px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        `;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = id;
        checkbox.style.cssText = `
            width: 16px;
            height: 16px;
            margin-right: 10px;
            cursor: pointer;
        `;

        const text = document.createElement('span');
        text.innerText = labelText;
        text.style.cssText = `
            font-size: 13px;
            font-weight: normal;
            color: #333;
            user-select: none;
        `;

        label.appendChild(checkbox);
        label.appendChild(text);
        container.appendChild(label);

        // Hover effect
        label.addEventListener('mouseenter', function () {
            if (!checkbox.checked) {
                label.style.borderColor = '#666';
                label.style.backgroundColor = '#fafafa';
            }
        });

        label.addEventListener('mouseleave', function () {
            if (!checkbox.checked) {
                label.style.borderColor = '#ccc';
                label.style.backgroundColor = 'white';
            }
        });

        // Checked state styling - Black monochrome theme
        checkbox.addEventListener('change', function () {
            if (checkbox.checked) {
                label.style.borderColor = '#000';
                label.style.backgroundColor = '#333';
                text.style.color = 'white';
                text.style.fontWeight = 'bold';
            } else {
                label.style.borderColor = '#ccc';
                label.style.backgroundColor = 'white';
                text.style.color = '#333';
                text.style.fontWeight = 'normal';
            }
        });

        return { container, checkbox, label, text };
    }

    function applyDjangoAdminStyling(row) {
        if (row) {
            row.style.borderTop = 'none';
        }
    }

    const catCheckbox = catOption.checkbox;
    const prodCheckbox = prodOption.checkbox;

    // State management
    function updateVisibility(mode) {
        if (mode === 'category') {
            categoryRow.style.display = '';
            productRow.style.display = 'none';
            catCheckbox.checked = true;
            prodCheckbox.checked = false;

            // Trigger styling update
            catCheckbox.dispatchEvent(new Event('change'));
            prodCheckbox.dispatchEvent(new Event('change'));
        } else if (mode === 'product') {
            categoryRow.style.display = 'none';
            productRow.style.display = '';
            catCheckbox.checked = false;
            prodCheckbox.checked = true;

            // Trigger styling update
            catCheckbox.dispatchEvent(new Event('change'));
            prodCheckbox.dispatchEvent(new Event('change'));
        } else {
            // Neither checked - hide both
            categoryRow.style.display = 'none';
            productRow.style.display = 'none';
            catCheckbox.checked = false;
            prodCheckbox.checked = false;

            // Trigger styling update
            catCheckbox.dispatchEvent(new Event('change'));
            prodCheckbox.dispatchEvent(new Event('change'));
        }
    }

    // Checkbox event handlers
    catCheckbox.addEventListener('click', function (e) {
        if (this.checked) {
            updateVisibility('category');
        } else {
            categoryRow.style.display = 'none';
            catCheckbox.dispatchEvent(new Event('change'));
        }
    });

    prodCheckbox.addEventListener('click', function (e) {
        if (this.checked) {
            updateVisibility('product');
        } else {
            productRow.style.display = 'none';
            prodCheckbox.dispatchEvent(new Event('change'));
        }
    });

    // Initialize based on existing data
    const catSelect = document.querySelector('#id_categories');
    const prodSelect = document.querySelector('#id_products');
    const catSelectTo = document.querySelector('#id_categories_to');
    const prodSelectTo = document.querySelector('#id_products_to');

    let hasCat = false;
    let hasProd = false;

    if (catSelect && catSelect.selectedOptions.length > 0) hasCat = true;
    if (prodSelect && prodSelect.selectedOptions.length > 0) hasProd = true;
    if (catSelectTo && catSelectTo.options.length > 0) hasCat = true;
    if (prodSelectTo && prodSelectTo.options.length > 0) hasProd = true;

    if (hasProd) {
        updateVisibility('product');
    } else if (hasCat) {
        updateVisibility('category');
    } else {
        // Default to category for new forms
        updateVisibility('category');
    }
});
