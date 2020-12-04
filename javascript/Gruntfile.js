module.exports = function(grunt) {
    grunt.initConfig({
	uglify: {
	    
	    homepage: {
		options: {
		    banner: '$(document).ready(function() {',
		    footer: '});'
		},
		src: [ 
		    "src/modules/django-setup.js",
		    "src/modules/menu-opener.js",
		],
		dest: "../baskervilleweb/static/js/default.min.js"
	    },

	    form: {
		options: {
		    banner: '$(document).ready(function() {',
		    footer: '});'
		},
		src: [ 
		    "src/modules/django-setup.js",
		    "src/modules/menu-opener.js",
		    "src/modules/form-validation.js",
		],
		dest: "../baskervilleweb/static/js/form.min.js"
	    },

	    lib: {
		// Grunt will search for "**/*.js" under "lib/" when the "uglify" task
		// runs and build the appropriate src-dest file mappings then, so you
		// don't need to update the Gruntfile when files are added or removed.
		files: [
		    {
			expand: true,     // Enable dynamic expansion.
			cwd: 'src/lib/',      // Src matches are relative to this path.
			src: ['**/*.js'], // Actual pattern(s) to match.
			dest: '../baskervilleweb/static/js/lib/',   // Destination path prefix.
			ext: '.min.js',   // Dest filepaths will have this extension.
			extDot: 'first'   // Extensions in filenames begin after the first dot
		    },
		],
	    },
	},
    });
 // Load the plugin that provides the "uglify" task.
//    grunt.file.setBase('/home/chiara');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    
    // Default task(s).
    grunt.registerTask('default', ["concat",'uglify']);

};

//browser-stat.js  django-setup.js
