// Welcome to your new JavaScript file
console.log('Hello, World!');

// Example function
function greet(name) {
    return `Hello, ${name}!`;
}

// Example usage
const message = greet('Developer');
console.log(message);

// Export for use in other modules (if using Node.js)
module.exports = {
    greet
};