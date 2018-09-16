pipeline {
    agent none
    stages {
        stage('Test') {
	    agent {
	        docker {
		    image 'qnib/pytest'
		}
	    }
	    steps {
	        sh 'python -m unittest tests.unit_tests'
	    }
	}
    }
}