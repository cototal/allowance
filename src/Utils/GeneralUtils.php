<?php

namespace App\Utils;

class GeneralUtils
{
    /**
     * @param string|int $key
     * @param array $array
     */
    public static function emptyKeyValue($key, array $array)
    {
        return !array_key_exists($key, $array) || empty($array[$key]);
    }
}