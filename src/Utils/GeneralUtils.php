<?php

namespace App\Utils;

class GeneralUtils
{
    public static function emptyKeyValue(string|int $key, array $array): bool
    {
        return !array_key_exists($key, $array) || empty($array[$key]);
    }
}