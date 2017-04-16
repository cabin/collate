angular.module('collate.controllers', [])

  .controller 'AuthCtrl', ($scope) ->
    $http.get('/auth/current')
    $scope.user = null
