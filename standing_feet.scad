// Define the triangle points
A = [0, 0];
B = [3.2, 0];
// C = [0.2102, 2];
// D = [0.6102, 1.732];
C = [0.1366, 1.3];
D = [0.582, 1.5];
E = [0.7602, 1.632];
F = [0.4526, 0.5];
G = [0.626, 0.5];

points = [A, B, E, G, F, D, C];

// Function to create the scaled and extruded object
module createObject() {
    scale([10, 10, 10])
    linear_extrude(height = 0.8)  // Ensure height is also scaled
        polygon(points);
}

// Create the first object
createObject();

// Create the second object with an offset
translate([0, 25, 0]) // Adjust the X offset as needed
    createObject();


